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
from latin_translator.service.translation import TranslationService
from latin_translator.service.orchestrator import TranslationOrchestrator

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

# %%
from latin_translator.service.epub_builder import EpubBuilder, EpubConfig
from pathlib import Path
from datetime import datetime

# %%
logger.info("Creating multi-letter EPUB with custom configuration")
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
letter = all_letters[letter_index]

# Initialize translation service
translation_service = TranslationService(TranslationOrchestrator())

logger.info(f"Translating letter {letter.roman} ({letter.number}): {letter.title}")
translation_stages = translation_service.translate_letter(letter)
translated_text = "\n\n".join([" ".join(stage.rhetorical) for stage in translation_stages])
# %%
logger.info("Displaying translation stages")
TranslationStages.display_many(translation_stages)