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
from latin_translator.utils.logging_config import LoggingManager

# Initialize logging
logging_manager = LoggingManager()
logging_manager.configure_base_logging()

# Uncomment the line below to enable detailed OpenAI API request logging
#logging_manager.configure_openai_logging(enable=True)

logger = logging_manager.get_notebook_logger('translate_letter')
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
all_letters = downloader.fetch_all_letters()

# Select a letter by index (e.g., letter 1)
letter_index = 0  # Change this to select different letters
letter = all_letters[letter_index]

display(Markdown(f"**Original Letter {letter.roman} ({letter.number}): {letter.title}**\n\n{letter.content}"))

# %%
# Translate the letter
translation_service = TranslationService(TranslationOrchestrator())
translation = translation_service.translate_letter(letter)

# Display the translation
translated_text = "\n\n".join([" ".join(para["sentences"]) for para in translation])
display(Markdown(f"**Translation:**\n\n{translated_text}"))