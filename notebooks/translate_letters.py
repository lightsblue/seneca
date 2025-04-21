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
from latin_translator.models import Letter, TranslationStages
from latin_translator.service.letter_translator import LetterTranslator

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
# logging.getLogger('latin_translator.service.letter_translator.http').setLevel(logging.DEBUG)
# logging.getLogger('latin_translator.service.letter_translator').setLevel(logging.DEBUG)
# %%
# Load .env file from project root
load_dotenv()

# Verify API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

# %%
# Import reload to refresh modules after code changes
import importlib
import latin_translator.service.letter_translator
# import latin_translator.service.translation # Keep this removed

# Function to reload modules after changes
#def reload_modules():
#    importlib.reload(latin_translator.service.letter_translator) # Updated reload
#    # importlib.reload(latin_translator.service.translation) # Remove reload
#    logger.info("Modules reloaded successfully")

# Run this cell after making changes to core modules
#reload_modules()

# %%
from latin_translator.models import Letter
from latin_translator.service.letter_translator import LetterTranslator
from latin_translator.service.seneca_letter_downloader import SenecaLetterDownloader
from IPython.display import display, Markdown

# %%
downloader = SenecaLetterDownloader()  # Uses default URLs
logger.info("Fetching all letters...")
all_letters = downloader.fetch_all_letters()
logger.info(f"Found {len(all_letters)} letters")
# %%
from latin_translator.service.epub_builder import EpubBuilder, EpubConfig
from pathlib import Path
from datetime import datetime

# %%
# Create an EPUB with multiple letters and custom configuration
logger.info("Creating multi-letter EPUB with custom configuration")
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Get letter 2 only (index 1)
letters_to_include = all_letters[80:83]  # [start:end] is exclusive of end, so this gets just one letter

# Get letter range for title
letter_range = f"Letters {letters_to_include[0].number}-{letters_to_include[-1].number}"
logger.info(f"Including {len(letters_to_include)} letters in the EPUB: {letter_range}")
# %%
# Initialize translation service
translator = LetterTranslator()

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
    translation_stages = translator.process_letter(letter_to_add.content)
    # Use the rhetorical translation for the EPUB
    translated_text = "\n\n".join([" ".join(stage.rhetorical) for stage in translation_stages])
    
    # Add to EPUB
    builder.add_letter(letter_to_add, translated_text)

# Save the EPUB
custom_epub_path = builder.save(Path("seneca_volume_1.epub"))
logger.info(f"Created multi-letter EPUB at: {custom_epub_path}")
# %%
