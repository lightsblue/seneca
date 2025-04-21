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
# Select a letter by number (e.g., letter 77)
# Change this to select a different letter number
letter = downloader.get_letter_by_number(77)
logger.info(f"Selected letter {letter.roman} ({letter.number}): {letter.title}")

# %%
from latin_translator.service.epub_builder import EpubBuilder, EpubConfig
from pathlib import Path
from datetime import datetime

# %%
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
logger.info(f"Translating letter {letter.roman} ({letter.number}): {letter.title}")
# %%
print(letter.sections[6])
# %%
# Initialize translation service
translator = LetterTranslator()
translation_stages = translator.process_letter(letter.sections[6])
translated_text = "\n\n".join([" ".join(stage.rhetorical) for stage in translation_stages])
# %%
logger.info("Displaying translation stages")
TranslationStages.display_many(translation_stages)