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

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('translate_letter')

# Configure library loggers to reduce noise
logging.getLogger('httpx').setLevel(logging.WARNING)

# Optionally enable OpenAI debug logging
# Uncomment to enable detailed request logging
# logging.getLogger('latin_translator.service.orchestrator.http').setLevel(logging.DEBUG)
# logging.getLogger('latin_translator.service.orchestrator').setLevel(logging.DEBUG)
# %%
# Load .env file from project root
load_dotenv()

# Verify API key is loaded
if not os.getenv("OPENAI_API_KEY"):
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
from latin_translator.service.seneca_letter_downloader import SenecaLetterDownloader
from IPython.display import display, Markdown

# %%
downloader = SenecaLetterDownloader()  # Uses default URLs
logger.info("Fetching all letters...")
all_letters = downloader.fetch_all_letters()
logger.info(f"Found {len(all_letters)} letters")

# Select a letter by index (e.g., letter 1)
letter_index = 0  # Change this to select different letters
letter = all_letters[letter_index]
logger.info(f"Selected letter {letter.roman} ({letter.number}): {letter.title}")

display(Markdown(f"**Original Letter {letter.roman} ({letter.number}): {letter.title}**\n\n{letter.content}"))
# %%
from latin_translator.service.epub_builder import EpubBuilder, EpubConfig
from pathlib import Path
from datetime import datetime

# %%
# Create an EPUB with multiple letters and custom configuration
logger.info("Creating multi-letter EPUB with custom configuration")
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Get first three letters
letters_to_include = all_letters[77:80]  # Letters are 0-indexed, so letter 77 is at index 76
logger.info(f"Including {len(letters_to_include)} letters in the EPUB")

# Get letter range for title
letter_range = f"Letters {letters_to_include[0].number}-{letters_to_include[-1].number}"

# Initialize translation service
translation_service = TranslationService(TranslationOrchestrator())

# Create builder with custom config
custom_config = EpubConfig(
    title_template=f"Letters of Seneca ({letter_range}) - {timestamp}",
    author="Lucius Annaeus Seneca"
)

# Create builder with custom config
builder = EpubBuilder(config=custom_config)

# Add each letter
for letter_to_add in letters_to_include:
    # Translate the letter
    logger.info(f"Translating letter {letter_to_add.roman} for EPUB")
    translation = translation_service.translate_letter(letter_to_add)
    translated_text = "\n\n".join([" ".join(para["sentences"]) for para in translation])
    
    # Add to EPUB
    builder.add_letter(letter_to_add, translated_text)

# Save the EPUB
custom_epub_path = builder.save(Path("seneca_volume_1.epub"))
logger.info(f"Created multi-letter EPUB at: {custom_epub_path}")
# %%
