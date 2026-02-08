# Country Size Calculator

This is a python script that calculates the land areas for an equirectangular map assuming that each country is colour-coded uniquely, accounting for distortion at higher latitudes.

### Basic Usage

#### Requirements for this script
1. Ensure that the map is an equirectangular projection.
2. Each country is colour with a unique hexadecimal value (if there are two separate regions with the same value, they are considered part of the same country)
3. Ensure that the background (or water) is fully white #FFFFFF or (RGB: 255, 255, 255).

#### Running the script
1. Place your colour-coded map image in the same folder or have the full file path of the image ready
2. Run the script
```
  python country_size_calculator.py
```
3. Follow the interactive prompts:
  - Select your image file (listed in dot points if in same folder as script)
  - Specify the circumference at the equator of the map
  - NOT IMPLEMENTED YET:
    - the script assumes that the image is the entire map of your world's circumference. I plan to have another prompt to enable usage of this script for parts of a map instead of the entirety of a world.

4. Results are exported and saved to an excel file in the same folder named [image_name]_map_sizes.xlsx

The generated excel file contains the hex colour, pixel count, and area (km^2), and finally the totals for them.

### Examples

Testing it with a map of the real world and roughly colouring some states (at their peak), see example Equirectangular_Map_Example.png

```
  python country_size_calculator.py
  Image files found in this folder:
  1. Equirectangular_Map_Example.png
  Select an image file by number (1-3), or enter a custom path: 1
  Enter the equator circumference in kilometers (default 40075 km):
  ...
```

We get in the output file:

Hex Color | Pixel Count | Area (km^2)
#000000 |	40115 | 69893122.75
#761818 | 21596 | 33930370.61
#B82424 | 16300 | 16475961.09
#2F3EA9 | 6011	| 9002863.22
#3F3F3F | 3376 | 4660965.386
TOTAL | 87398	| 133963283.1

#761818 being the British Empire at its peak
#B82424 being modern day Russia
#2F3EA9 being USA
#3F3F3F being the Third Reich at its peak (minus modern day Russia)

These calculations are roughly 10% less than the actual, I'm not 100% sure yet why.
Russia is supposed to be 17.1 million km² whilst here its 16.4 million km².
On the other hand, the US is 9.0 million km² whilst its meant to be 9.8 million km².
Still working on it, please message me if you do find out why it's having some discrepancy and I can update.

### Limitations
- Only works with equirectangular projection maps, looking to add an option for mercator projection.
- Best results with solid colours - I plan on adding anti-aliasing adjustments to unique colours, but current a WIP.

### License
MIT License - feel free to use and modify for your projects.

