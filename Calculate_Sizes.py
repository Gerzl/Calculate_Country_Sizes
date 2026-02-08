import numpy as np
from PIL import Image
import pandas as pd
import os

def calculate_map_sizes(image_path, equator_circumference, output_file='map_sizes.xlsx'):
    """calculate land sizes from equirectangular map and export to Excel"""

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

    KM_PER_PIXEL = (equator_circumference / MAP_WIDTH) ** 2

    print(f"Equator circumference: {equator_circumference:,.2f} km")
    print(f"Km per pixel: {equator_circumference / MAP_WIDTH:.4f} km")
    print(f"Area per pixel (equator): {KM_PER_PIXEL:.4f} km²\n")

    img_array = np.array(img)

    print("Adjusting for latitude...")
    y_coords = np.arange(MAP_HEIGHT)

    latitudes = 90 - (y_coords / MAP_HEIGHT) * 180
    area_adjustments = KM_PER_PIXEL * np.cos(np.radians(latitudes))
    area_weights = np.repeat(area_adjustments[:, np.newaxis], MAP_WIDTH, axis=1)

    print("Processing pixels...")
    color_ids = (img_array[:, :, 0].astype(np.uint32) << 16) + \
                (img_array[:, :, 1].astype(np.uint32) << 8) + \
                img_array[:, :, 2].astype(np.uint32)

    land_mask = color_ids != 0xFFFFFF
    unique_colors = np.unique(color_ids[land_mask])

    print(f"Found {len(unique_colors)} unique colors\n")

    data = []
    for i, color_id in enumerate(unique_colors):
        mask = color_ids == color_id
        pixels = int(np.sum(mask))
        area = np.sum(area_weights[mask])

        r = (color_id >> 16) & 0xFF
        g = (color_id >> 8) & 0xFF
        b = color_id & 0xFF
        hex_color = f"#{r:02X}{g:02X}{b:02X}"

        data.append({
            'Hex Color': hex_color,
            'Pixel Count': pixels,
            'Area (km²)': area
        })

        if (i + 1) % 10 == 0 or (i + 1) == len(unique_colors):
            print(f"Processed {i + 1}/{len(unique_colors)} colors")

    df = pd.DataFrame(data)
    df = df.sort_values(by='Area (km²)', ascending=False).reset_index(drop=True)
    df.index += 1

    total_pixels = np.sum(land_mask)
    total_area = np.sum(area_weights[land_mask])

    totals = pd.DataFrame([{
        'Hex Color': 'TOTAL',
        'Pixel Count': total_pixels,
        'Area (km²)': total_area
    }])

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
    print(f"Total land area: {total_area:,.2f} km²\n")

    return df

def main():

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

    equator_circumference = input("Enter the equator circumference in kilometers (default 40075 km): ")

    if equator_circumference.strip() == "":
        equator_circumference = 40075
    else:
        try:
            equator_circumference = float(equator_circumference)
        except ValueError:
            print("Invalid input for equator circumference. Using default value of 40075 km.")
            equator_circumference = 40075

    output_filename = f"{os.path.splitext(map_filename)[0]}map_sizes.xlsx"

    result = calculate_map_sizes(map_filename, equator_circumference, output_filename)

    if result is not None:
        print("Script complete.")
    else:
        print("Script failed.")

if __name__ == "__main__":
    main()








