# beatoraja-seg-display
A Pygame-based display tool inspired by [kinetic-flow/iidxseg](https://github.com/kinetic-flow/iidxseg)

## Features
- **Special Character Mapping**: Converts special characters to readable alternatives.
- **Transliteration**: Converts Japanese titles to Romanized text.


## Requirements
- Python 3.7+
- [DSEG14Classic-Italic font](https://github.com/keshikan/DSEG)

## Installation
- Install dependencies from `requirements.txt`
- Replace `"C:/path/to/your/beatoraja_log.xml"` with the path to your actual log file in the beatoraja main directory.
- After starting one of the two files, change the song once in-game to update the display.

## Customization
- `ON_COLOR = (255, 0, 0)`  # Text color (default: red)
- `BG_COLOR = (0, 0, 0)`    # Background color (default: black)
- `font = pygame.font.Font(font_path, 72)`  # Default: 72
- `FPS = 5`  # Frames per second (default: 5)
- `DISPLAY_LENGTH = 9`  # Default: 9
