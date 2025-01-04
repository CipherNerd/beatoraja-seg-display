
import os
import time
import re
import sys
import subprocess
import pygame
import pykakasi


# Path to the log file
LOG_FILE_PATH = "C:/path/to/your/beatoraja_log.xml"

if not os.path.exists(LOG_FILE_PATH):
    print(f"Error: Log file not found at {LOG_FILE_PATH}")
    sys.exit(0)

pygame.init()
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 150
ON_COLOR = (255, 0, 0)
OFF_COLOR = (20, 20, 20)
BG_COLOR = (0, 0, 0)
FONT_NAME = "dseg14classic-italic"
font_path = pygame.font.match_font(FONT_NAME)
DISPLAY_LENGTH = 9
FPS = 5

if not font_path:
    print(f"Error: Font '{FONT_NAME}' not found on the system. Please ensure it's installed.")
    sys.exit(1)

font = pygame.font.Font(font_path, 72)

kakasi = pykakasi.kakasi()
kakasi.setMode("H", "a")
kakasi.setMode("K", "a")
kakasi.setMode("J", "a")
kakasi.setMode("r", "Hepburn")
converter = kakasi.getConverter()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("IIDX Segment Display - reading BMS/BME file")
clock = pygame.time.Clock()

SPECIAL_CHAR_MAP = {
    '☆': '*', '★': '*', '♪': '~', '⇒': '->', '∀': 'A', '∃': 'E',
    '℃': ' deg C', '∞': 'Infinity', '∑': 'E', '⊂': '(sub)', '∈': '(in)',
    '∩': '(and)', '∪': '(or)', '♥': '<3', '❤': '<3', '❥': '<3',
    'Ʞ': 'K', 'И': 'N', 'ᴚ': 'R', 'Ꞷ': 'W', '【': '[', '】': ']',
    '『': '[', '』': ']', '・': '.', '≡': '=', '≠': '!=', '≥': '>=',
    '≤': '<=', '∂': 'd', '∇': 'Delta', '±': '+/-', '⁰': '0', '¹': '1',
    '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7',
    '⁸': '8', '⁹': '9', '∑': 'E', '∀': 'A', '♡': '<3', 'R∞tAge': 'RootAge',
    '%': 'pct', '&': '(and)', '-': '-', 'X-DEN': 'KAI-DEN',
}

def clean_special_characters(text):
    cleaned_text = ""
    for char in text:
        if char in SPECIAL_CHAR_MAP:
            cleaned_text += SPECIAL_CHAR_MAP[char]
        elif char.isalnum() or char.isspace():
            cleaned_text += char
        else:
            cleaned_text += " "
    return cleaned_text

def transliterate_title(title):
    title = clean_special_characters(title)
    try:
        return converter.do(title)
    except Exception as e:
        print(f"Error transliterating title: {e}")
        return title

def extract_message(record):
    match = re.search(r"<message>(.*?)</message>", record, re.DOTALL)
    return match.group(1) if match else None

def extract_title_from_bms_file(file_path):
    """
    Extract the #TITLE field directly from the .bms or .bme file.
    """
    print(f"Attempting to read title from: {file_path}")  # Debugging
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="shift_jis", errors="ignore") as file:
                for line in file:
                    if line.strip().startswith("#TITLE"):
                        title = line.split(" ", 1)[1].strip()
                        print(f"Title found in file '{file_path}': {title}")  # Debugging
                        return title
        else:
            print(f"File does not exist: {file_path}")  # Debugging
    except Exception as e:
        print(f"Error reading title from file '{file_path}': {e}")
    return None


def extract_title_from_message(message):
    """
    Extract the title by reading the .bms or .bme file mentioned in the log message.
    """
    try:
        # Extract the file path from the message
        match = re.search(r"(.*?\.(bms|bme))", message)
        if match:
            file_path = match.group(1)
            title = extract_title_from_bms_file(file_path)
            if title:
                return title
            else:
                print(f"Failed to extract title from: {file_path}")
    except Exception as e:
        print(f"Error processing message: {e}")
    return None

def draw_text(text):
    screen.fill(BG_COLOR)
    char_width = WINDOW_WIDTH // DISPLAY_LENGTH
    x_offset = 0

    text = text.ljust(DISPLAY_LENGTH)

    for char in text:
        dimmed_surface = font.render("~", True, OFF_COLOR)
        dimmed_rect = dimmed_surface.get_rect(midtop=(x_offset + char_width // 2, 50))
        screen.blit(dimmed_surface, dimmed_rect)

        if char.strip():
            active_surface = font.render(char, True, ON_COLOR)
            active_rect = active_surface.get_rect(midtop=(x_offset + char_width // 2, 50))
            screen.blit(active_surface, active_rect)

        x_offset += char_width

def scroll_text_loop(full_text):
    if len(full_text) < DISPLAY_LENGTH:
        full_text = full_text.center(DISPLAY_LENGTH)

    spaced_text = "  " + full_text + " " * 5
    repeated_text = spaced_text * 3
    offset = 0

    while True:
        display_text = repeated_text[offset:offset + DISPLAY_LENGTH]
        draw_text(display_text)
        offset += 1
        if offset >= len(spaced_text):
            offset = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(FPS)
        yield

def monitor_log_file():
    """Monitor the log file for updates and update the display."""
    last_title = None
    current_record = ""

    try:
        with open(LOG_FILE_PATH, "r", encoding="shift_jis", errors="ignore") as file:
            file.seek(0, os.SEEK_END)
            text_scroller = None

            while True:
                line = file.readline()
                if not line:
                    if text_scroller:
                        try:
                            next(text_scroller)
                        except StopIteration:
                            pass
                    pygame.display.flip()
                    clock.tick(FPS)
                    continue

                current_record += line
                if "</record>" in line:
                    message = extract_message(current_record)
                    if message:
                        title = extract_title_from_message(message)
                        if title and title != last_title:
                            transliterated_title = transliterate_title(title)
                            last_title = transliterated_title
                            text_scroller = scroll_text_loop(transliterated_title)
                            next(text_scroller)
                    current_record = ""
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    monitor_log_file()
