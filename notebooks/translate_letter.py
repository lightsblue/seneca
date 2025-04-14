# %% [markdown]
# # Letter Translation Interface
# 
# This notebook provides a simple interface for translating Seneca's letters using our translation system.

# %%
# Load environment variables
from dotenv import load_dotenv
import os

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
    print("Modules reloaded successfully")

# Run this cell after making changes to core modules
reload_modules()

# %%
from latin_translator.models import Letter, TranslationRequest
from latin_translator.service.translation import TranslationService
from latin_translator.service.orchestrator import TranslationOrchestrator
from IPython.display import display, Markdown

# %%
# Initialize the translation service
orchestrator = TranslationOrchestrator()
translation_service = TranslationService(orchestrator)

# %%
# Example letter
letter = Letter(
    number=1,
    roman="I",
    title="On Saving Time",
    content="""Ita fac, mi Lucili: vindica te tibi, et tempus quod adhuc aut auferebatur aut subripiebatur aut excidebat collige et serva. Persuade tibi hoc sic esse ut scribo: quaedam tempora eripiuntur nobis, quaedam subducuntur, quaedam effluunt. Turpissima tamen est iactura quae per neglegentiam fit."""
)

# Display the original letter
display(Markdown(f"**Original Letter {letter.roman} ({letter.number}): {letter.title}**\n\n{letter.content}"))

# %%
# Create translation request
request = TranslationRequest(
    text=letter.content,
    instructions="Translate this letter from Latin to English, preserving Seneca's philosophical precision."
)

# Translate the letter
translation = translation_service.translate_letter(letter, request)

# Display the translation
translated_text = "\n\n".join([" ".join(para["sentences"]) for para in translation])
display(Markdown(f"**Translation:**\n\n{translated_text}")) 