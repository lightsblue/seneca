# %% [markdown]
# # Letter Translation Interface
# 
# This notebook provides a simple interface for translating Seneca's letters using our translation system.

# %%
# Load environment variables
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from typing import List
import logging

# Configure logging to display in the notebook
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set the log level for the 'httpx' logger to WARNING immediately after importing logging
logging.getLogger('httpx').setLevel(logging.WARNING)

# Create logger for this notebook
logger = logging.getLogger('translate_letter')
logger.setLevel(logging.INFO)

# Function to enable detailed OpenAI API request logging
def enable_openai_debug_logs():
    # Enable HTTP request/response logging
    http_logger = logging.getLogger('latin_translator.service.orchestrator.http')
    http_logger.setLevel(logging.DEBUG)
    
    # Enable general orchestrator logging
    orchestrator_logger = logging.getLogger('latin_translator.service.orchestrator')
    orchestrator_logger.setLevel(logging.DEBUG)
    
    logger.info("OpenAI debug logging enabled - you'll see detailed HTTP request and response information")

# Function to disable detailed logging
def disable_openai_debug_logs():
    logging.getLogger('latin_translator.service.orchestrator.http').setLevel(logging.WARNING)
    logging.getLogger('latin_translator.service.orchestrator').setLevel(logging.INFO)
    logger.info("OpenAI debug logging disabled")

# %%
# Uncomment the line below to enable detailed OpenAI API request logging
#enable_openai_debug_logs()

# Load .env file from project root
load_dotenv()

# Verify API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

# %%
# Import reload to refresh modules after code changes
import importlib
import latin_translator.service.orchestrator
import latin_translator.service.translation

# Function to reload modules after changes
def reload_modules():
    importlib.reload(latin_translator.service.orchestrator)
    importlib.reload(latin_translator.service.translation)
    logger.info("Modules reloaded successfully")

# Run this cell after making changes to core modules
reload_modules()

# %%
from latin_translator.models import Letter
from latin_translator.service.translation import TranslationService
from latin_translator.service.orchestrator import TranslationOrchestrator
from IPython.display import display, Markdown

# %%
# Functions to download and parse Seneca's letters
def download_content(url: str) -> str:
    """Download content from a given URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def roman_to_int(roman: str) -> int:
    """Convert Roman numeral to integer."""
    roman = roman.upper()
    roman_numerals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    result = 0
    prev_value = 0
    for c in reversed(roman):
        if c not in roman_numerals:
            raise ValueError(f"Invalid Roman numeral character: {c}")
        value = roman_numerals[c]
        if value < prev_value:
            result -= value
        else:
            result += value
            prev_value = value
    return result

def extract_letters(content: str) -> List[Letter]:
    """Extract letters from HTML content."""
    soup = BeautifulSoup(content, 'html.parser')
    body = soup.find('body')
    letters: List[Letter] = []
    current_letter_number = None
    current_letter_roman = None
    current_letter_title = None
    current_letter_content: List[str] = []
    collecting = False

    for tag in body.find_all('p'):
        b_tag = tag.find('b')
        if b_tag:
            if current_letter_number is not None:
                letters.append(Letter(
                    number=current_letter_number,
                    roman=current_letter_roman,
                    title=current_letter_title or "",
                    content='\n'.join(current_letter_content).strip()
                ))

            title_text = b_tag.get_text(strip=True)
            parts = title_text.split('.', 1)
            if len(parts) == 2:
                roman_part = parts[0].strip()
                try:
                    number = roman_to_int(roman_part)
                    title_remainder = parts[1].strip()
                    current_letter_number = number
                    current_letter_roman = roman_part
                    current_letter_title = title_remainder
                    current_letter_content = []
                    collecting = True
                except ValueError:
                    collecting = False
                    current_letter_number = None
                    current_letter_title = None
            else:
                collecting = False
        elif tag.get('class') and 'shortborder' in tag.get('class'):
            if current_letter_number is not None:
                letters.append(Letter(
                    number=current_letter_number,
                    roman=current_letter_roman,
                    title=current_letter_title or "",
                    content='\n'.join(current_letter_content).strip()
                ))
            current_letter_number = None
            current_letter_title = None
            current_letter_content = []
            collecting = False
        elif collecting:
            current_letter_content.append(tag.get_text())

    if current_letter_number is not None and current_letter_content:
        letters.append(Letter(
            number=current_letter_number,
            roman=current_letter_roman,
            title=current_letter_title or "",
            content='\n'.join(current_letter_content).strip()
        ))

    return letters

# %%
# Download and parse letters
urls = [
    "https://www.thelatinlibrary.com/sen/seneca.ep1.shtml",
    "https://www.thelatinlibrary.com/sen/seneca.ep2.shtml",
    "https://www.thelatinlibrary.com/sen/seneca.ep3.shtml",
    "https://www.thelatinlibrary.com/sen/seneca.ep4.shtml",
    "https://www.thelatinlibrary.com/sen/seneca.ep5.shtml"
]

# Initialize the translation service
orchestrator = TranslationOrchestrator()
translation_service = TranslationService(orchestrator)

# Download and parse all letters
all_letters: List[Letter] = []
for url in urls:
    print(f"Processing {url}")
    try:
        content = download_content(url)
        letters = extract_letters(content)
        all_letters.extend(letters)
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")

print(f"Total letters collected: {len(all_letters)}")

# %%
# Select a letter by index (e.g., letter 1)
letter_index = 0  # Change this to select different letters
letter = all_letters[letter_index]

# Display the original letter
display(Markdown(f"**Original Letter {letter.roman} ({letter.number}): {letter.title}**\n\n{letter.content}"))

# %%
# Translate the letter
translation = translation_service.translate_letter(letter)

# Display the translation
translated_text = "\n\n".join([" ".join(para["sentences"]) for para in translation])
display(Markdown(f"**Translation:**\n\n{translated_text}"))