# Sprite Sheet Generator

A Blender addon that converts image sequences into sprite sheets. Perfect for game development, animation exports, and texture atlases.

## Features

- **Batch Processing**: Load entire folders of images automatically
- **Smart Sorting**: Natural sorting handles frame numbers correctly (frame1, frame2, ... frame10, frame11)
- **Flexible Grid Layout**: 
  - Set specific columns/rows
  - Auto-calculate optimal grid dimensions
- **Filename Filtering**: Filter images by name pattern (e.g., "walk" to only include walk_001.png, walk_002.png, etc.)
- **Padding Control**: Add pixel padding between sprites
- **Scale Output**: Scale sprites from 10% to 400%
- **Reverse Order**: Option to reverse the sequence order
- **Multiple Formats**: Export as PNG, JPEG, TGA, or BMP

## Installation

1. Download or clone this repository
2. Zip the `SpriteSheetGenerator` folder (the folder containing `__init__.py`)
3. In Blender, go to **Edit > Preferences > Add-ons**
4. Click **Install...** and select the zip file
5. Enable the addon by checking the checkbox next to "Import-Export: Sprite Sheet Generator"

## Usage

1. Open the **3D Viewport** sidebar (press `N` if hidden)
2. Navigate to the **Sprite Sheet** tab
3. Configure your settings:

### Source Settings
- **Source Directory**: Select the folder containing your image sequence
- **Filename Filter**: (Optional) Filter files by name pattern
- **Scan Directory**: Preview how many images will be processed

### Grid Layout
- **Columns**: Number of columns (0 = auto-calculate)
- **Rows**: Number of rows (0 = auto-calculate)
- **Padding**: Pixels between each sprite

### Transform
- **Scale %**: Scale factor for output (100 = original size)
- **Reverse Order**: Reverse the sequence order

### Output
- **Output Format**: PNG, JPEG, TGA, or BMP
- **Output Path**: Where to save the sprite sheet (use `//` for relative paths)

4. Click **Generate Sprite Sheet**

## Supported Image Formats

Input images can be any of the following formats:
- PNG
- JPEG/JPG
- TGA
- BMP
- TIFF/TIF
- EXR

## Tips

- Use **Scan Directory** before generating to verify the correct images are found
- Set columns OR rows to 0 to auto-calculate that dimension
- Set both to 0 for an automatically calculated near-square grid
- PNG format preserves transparency for sprites with alpha channels
- Use `//spritesheet.png` as the output path to save next to your .blend file

## Example Workflow

1. Render an animation as an image sequence (e.g., `frame_001.png` to `frame_024.png`)
2. Set **Source Directory** to the render output folder
3. Leave columns/rows at 0 for auto-layout, or set **Columns** to 6 for a 6x4 grid
4. Set output path and format
5. Generate!

## Requirements

- Blender 4.0 or later

## License

MIT License - Feel free to use and modify as needed.
