# Country Size Calculator

This is a python script that calculates the land areas for an equirectangular map assuming that each country is colour-coded uniquely, accounting for distortion at higher latitudes.

## Features

- **Area Calculation**: Accurately calculates land areas from equirectangular maps with latitude distortion correction
- **Population Counting**: Optional feature to count population based on white pixels in a separate population density map
- **Custom Map Bounds**: Support for partial map regions (e.g., 0°N to 80°N, 80°W to 40°W) instead of only full world maps
- **Excel Export**: Results exported to Excel with color codes, pixel counts, areas, and optional population data

### Basic Usage

#### Requirements for this script
1. Ensure that the map is an equirectangular projection.
2. Each country is colour with a unique hexadecimal value (if there are two separate regions with the same value, they are considered part of the same country)
3. Ensure that the background (or water) is fully white #FFFFFF or (RGB: 255, 255, 255).

#### Running the script
1. Place your colour-coded map image in the same folder or have the full file path of the image ready
2. Run the script
```bash
python Calculate_Sizes.py
```
3. Follow the interactive prompts:
   - Select your image file (listed in dot points if in same folder as script)
   - Specify the circumference at the equator of the map (default: 40075 km for Earth)
   - **NEW**: Choose whether your map covers only a partial region
     - If yes, specify the latitude and longitude bounds (e.g., Lat: 0° to 80°, Lon: -80° to 40°)
   - **NEW**: Choose whether to include population data
     - If yes, provide a population density map where white pixels represent population
     - Specify how many people each white pixel represents (default: 10,000)

4. Results are exported and saved to an excel file in the same folder named [image_name]map_sizes.xlsx

The generated excel file contains:
- **Hex Color**: The unique color code for each country/region
- **Pixel Count**: Number of pixels in that color
- **Area (km²)**: Calculated area accounting for latitude distortion
- **Population** (optional): Estimated population if a population map was provided
- **TOTAL**: Summary row with totals for all columns

### Examples

#### Example 1: Basic Usage (Full World Map)

Testing it with a map of the real world and roughly colouring some states (at their peak), see example Equirectangular_Map_Example.png

```bash
python Calculate_Sizes.py
Image files found in this folder:
1. Equirectangular_Map_Example.png
Select an image file by number (1-1), or enter a custom path: 1
Enter the equator circumference in kilometers (default 40075 km):

Does this map cover only a partial region (not full world)? (y/n, default n): n

Do you have a population density map to analyze? (y/n, default n): n
...
```

We get in the output file:

| Hex Color | Pixel Count | Area (km²) | 
| --- | --- | --- |
| #000000 | 40115 | 69893122.75 |
| #761818 | 21596 | 33930370.61 | 
| #B82424 | 16300 | 16475961.09 | 
| #2F3EA9 | 6011 | 9002863.22 |
| #3F3F3F | 3376 | 4660965.386 |
| TOTAL | 87398 | 133963283.1 |

- #761818 being the British Empire at its peak
- #B82424 being modern day Russia
- #2F3EA9 being USA
- #3F3F3F being the Third Reich at its peak (minus modern day Russia)

#### Example 2: Partial Map with Custom Bounds

For a map covering only North America and Europe (0°N to 80°N, 80°W to 40°W):

```bash
Does this map cover only a partial region (not full world)? (y/n, default n): y

Enter the latitude and longitude bounds of your map:
  Minimum latitude (southernmost, default -90): 0
  Maximum latitude (northernmost, default 90): 80
  Minimum longitude (westernmost, default -180): -80
  Maximum longitude (easternmost, default 180): 40
```

#### Example 3: With Population Data

If you have a population density map where white pixels represent population centers:

```bash
Do you have a population density map to analyze? (y/n, default n): y
Enter the path to the population map image file: population_map.png
Enter the number of people per white pixel (default 10000): 10000
```

Output will include a Population column:

| Hex Color | Pixel Count | Area (km²) | Population |
| --- | --- | --- | --- |
| #000000 | 40115 | 69893122.75 | 5690000 |
| #761818 | 21596 | 33930370.61 | 2740000 |
| ... | ... | ... | ... |

### Limitations
- Only works with equirectangular projection maps
- Best results with solid colours - anti-aliasing may affect accuracy
- Population counting requires a separate population density map with white pixels

### Notes on Accuracy

These calculations are roughly 10% less than the actual values. For example:
- Russia is supposed to be 17.1 million km² whilst the calculation shows 16.4 million km²
- The US is 9.0 million km² whilst it's meant to be 9.8 million km²

If you find out why there's a discrepancy, please open an issue or submit a PR!

### Future Enhancements
- Additional projection compatibilities (e.g., Mercator projection)
- Anti-aliasing considerations for better edge detection
- More sophisticated population distribution models

### License
MIT License - feel free to use and modify for your projects.
