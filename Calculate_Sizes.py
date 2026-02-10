import numpy as np
from numpy.lib.stride_tricks import as_strided
from PIL import Image
import pandas as pd
import sys
import os

def calculate_map_sizes(image_path, equator_circumference, output_file='map_sizes.xlsx',
                        population_image_path=None, population_per_pixel=10000,
                        lat_min=-90, lat_max=90, lon_min=-180, lon_max=180):
    """calculate land sizes from equirectangular map and export to Excel
    
    Args:
        image_path: Path to the color-coded map image
        equator_circumference: Full equator circumference in km
        output_file: Excel output file name
        population_image_path: Optional path to population density map (white pixels = population)
        population_per_pixel: Number of people per white pixel (default: 10000)
        lat_min: Minimum latitude of the map region (default: -90)
        lat_max: Maximum latitude of the map region (default: 90)
        lon_min: Minimum longitude of the map region (default: -180)
        lon_max: Maximum longitude of the map region (default: 180)
    """

    print("\n" + "="*10)
    print("COUNTRY SIZE CALCULATOR\n")
    print("="*10 + "\n")

    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found!")
        print(f"Ensure the file is either in the same folder as this script or is the complete path to the file.")
        return None

    print(f"Loading: {image_path}")
    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

    MAP_WIDTH, MAP_HEIGHT = img.size
    print(f"Dimensions: {MAP_WIDTH}x{MAP_HEIGHT} pixels")

    # Calculate the actual longitude span of the map
    lon_span = lon_max - lon_min
    map_circumference = equator_circumference * (lon_span / 360)
    
    KM_PER_PIXEL = map_circumference / MAP_WIDTH
    AREA_PER_PIXEL = KM_PER_PIXEL ** 2

    print(f"Map region: Latitude [{lat_min}° to {lat_max}°], Longitude [{lon_min}° to {lon_max}°]")
    print(f"Full equator circumference: {equator_circumference:,.2f} km")
    print(f"Map circumference at equator: {map_circumference:,.2f} km")
    print(f"Km per pixel: {KM_PER_PIXEL:.4f} km")
    print(f"Area per pixel (equator): {AREA_PER_PIXEL:.4f} km²\n")

    img_array = np.array(img)

    print("Adjusting for latitude...")
    y_coords = np.arange(MAP_HEIGHT)

    # Map y coordinates to actual latitudes based on the map's latitude range
    latitudes = lat_max - (y_coords / MAP_HEIGHT) * (lat_max - lat_min)
    area_adjustments = AREA_PER_PIXEL * np.cos(np.radians(latitudes))
    area_weights = np.repeat(area_adjustments[:, np.newaxis], MAP_WIDTH, axis=1)

    print("Processing pixels...")
    color_ids = img_array[:, :, 0].astype(np.int64) * 65536 + img_array[:, :, 1].astype(np.int64) * 256 + img_array[:, :, 2].astype(np.int64)

    land_mask = color_ids != 0xFFFFFF
    unique_colors = np.unique(color_ids[land_mask])

    print(f"Found {len(unique_colors)} unique colors\n")

    # Load population image if provided
    population_array = None
    white_mask = None
    if population_image_path:
        print(f"Loading population map: {population_image_path}")
        try:
            pop_img = Image.open(population_image_path).convert('RGB')
            if pop_img.size != (MAP_WIDTH, MAP_HEIGHT):
                print(f"Warning: Population map size {pop_img.size} doesn't match country map size {(MAP_WIDTH, MAP_HEIGHT)}")
                print("Resizing population map to match...")
                pop_img = pop_img.resize((MAP_WIDTH, MAP_HEIGHT), Image.NEAREST)
            population_array = np.array(pop_img)
            # White pixels represent population
            white_mask = (population_array[:, :, 0] == 255) & (population_array[:, :, 1] == 255) & (population_array[:, :, 2] == 255)
            print(f"Found {np.sum(white_mask)} population pixels")
            print(f"Population per pixel: {population_per_pixel:,} people\n")
        except Exception as e:
            print(f"Error loading population image: {e}")
            print("Continuing without population data...\n")
            population_array = None
            white_mask = None

    data = []
    for i, color_id in enumerate(unique_colors):
        mask = color_ids == color_id
        pixels = int(np.sum(mask))
        area = np.sum(area_weights[mask])

        r = (color_id >> 16) & 0xFF
        g = (color_id >> 8) & 0xFF
        b = color_id & 0xFF
        hex_color = f"#{r:02X}{g:02X}{b:02X}"

        entry = {
            'Hex Color': hex_color,
            'Pixel Count': pixels,
            'Area (km²)': area
        }
        
        # Add population count if population map is provided
        if population_array is not None and white_mask is not None:
            # Count white pixels within this country's territory
            country_pop_pixels = np.sum(white_mask & mask)
            entry['Population'] = int(country_pop_pixels * population_per_pixel)
        
        data.append(entry)

        if (i + 1) % 10 == 0 or (i + 1) == len(unique_colors):
            print(f"Processed {i + 1}/{len(unique_colors)} colors")

    df = pd.DataFrame(data)
    df = df.sort_values(by='Area (km²)', ascending=False).reset_index(drop=True)
    df.index += 1

    total_pixels = np.sum(land_mask)
    total_area = np.sum(area_weights[land_mask])

    totals_dict = {
        'Hex Color': 'TOTAL',
        'Pixel Count': total_pixels,
        'Area (km²)': total_area
    }
    
    if population_array is not None and white_mask is not None:
        total_population = int(np.sum(white_mask & land_mask) * population_per_pixel)
        totals_dict['Population'] = total_population

    totals = pd.DataFrame([totals_dict])

    df = pd.concat([df, totals], ignore_index=True)

    print("Exporting to Excel...")

    try:
        print(f"Exported results to '{output_file}'")
        df.to_excel(output_file, index=False, sheet_name='Map Sizes', engine='openpyxl')
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return None

    print("Done! Summary: ")
    print(f"Unique colours: {len(unique_colors)}")
    print(f"Total land pixels: {total_pixels:,}")
    print(f"Total land area: {total_area:,.2f} km²")
    if population_array is not None and white_mask is not None:
        print(f"Total population: {totals_dict['Population']:,} people")
    print()

    return df

def main():

    try:
        import openpyxl
    except ImportError:
        print("Warning: openpyxl not installed. Install with: pip install openpyxl")
        sys.exit(1)

    attempts = 0

    while attempts < 4:
        image_files = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]

        if image_files:
            print("Image files found in this folder:")
            for i, f in enumerate(image_files, 1):
                print(f"{i}. {f}")
            choice = input(f"Select an image file by number (1-{len(image_files)}), or enter a custom path: ")
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(image_files):
                    map_filename = image_files[choice_num - 1]
                else:
                    map_filename = choice
            except ValueError:
                map_filename = choice
        else:
            map_filename = input("Enter the path to the map image file: ")

        if os.path.exists(map_filename):
            break
        else:
            print(f"File '{map_filename}' not found. Please try again.\n")
            retry = input("Do you want to try again? (y/n): ").strip().lower()
            if retry != 'y':
                print("Exiting script.")
                return
            attempts += 1

    equator_circumference = input("Enter the equator circumference in kilometers (default 40075 km): ")

    if equator_circumference.strip() == "":
        equator_circumference = 40075
    else:
        try:
            equator_circumference = float(equator_circumference)
        except ValueError:
            print("Invalid input for equator circumference. Using default value of 40075 km.")
            equator_circumference = 40075

    # Ask for custom latitude/longitude bounds
    use_custom_bounds = input("\nDoes this map cover only a partial region (not full world)? (y/n, default n): ").strip().lower()
    
    lat_min, lat_max, lon_min, lon_max = -90, 90, -180, 180
    
    if use_custom_bounds == 'y':
        print("\nEnter the latitude and longitude bounds of your map:")
        try:
            lat_min_input = input("  Minimum latitude (southernmost, default -90): ").strip()
            lat_min = float(lat_min_input) if lat_min_input else -90
            
            lat_max_input = input("  Maximum latitude (northernmost, default 90): ").strip()
            lat_max = float(lat_max_input) if lat_max_input else 90
            
            lon_min_input = input("  Minimum longitude (westernmost, default -180): ").strip()
            lon_min = float(lon_min_input) if lon_min_input else -180
            
            lon_max_input = input("  Maximum longitude (easternmost, default 180): ").strip()
            lon_max = float(lon_max_input) if lon_max_input else 180
            
            print(f"\nUsing map bounds: Lat [{lat_min}° to {lat_max}°], Lon [{lon_min}° to {lon_max}°]")
        except ValueError:
            print("Invalid coordinate input. Using full world bounds.")
            lat_min, lat_max, lon_min, lon_max = -90, 90, -180, 180

    # Ask for population map
    use_population = input("\nDo you have a population density map to analyze? (y/n, default n): ").strip().lower()
    
    population_image_path = None
    population_per_pixel = 10000
    
    if use_population == 'y':
        pop_map_filename = input("Enter the path to the population map image file: ").strip()
        if os.path.exists(pop_map_filename):
            population_image_path = pop_map_filename
            pop_per_pixel_input = input("Enter the number of people per white pixel (default 10000): ").strip()
            if pop_per_pixel_input:
                try:
                    population_per_pixel = int(pop_per_pixel_input)
                except ValueError:
                    print("Invalid input. Using default value of 10000 people per pixel.")
        else:
            print(f"Population map file '{pop_map_filename}' not found. Continuing without population data.")

    output_filename = f"{os.path.splitext(map_filename)[0]}map_sizes.xlsx"

    result = calculate_map_sizes(map_filename, equator_circumference, output_filename,
                                  population_image_path, population_per_pixel,
                                  lat_min, lat_max, lon_min, lon_max)

    if result is not None:
        print("Script complete.")
    else:
        print("Script failed.")

if __name__ == "__main__":
    main()








