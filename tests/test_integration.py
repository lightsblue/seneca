import pytest
from pathlib import Path
from latin_translator.utils.mock_letter_source import MockLetterSource
from latin_translator.service.translation import TranslationService
from latin_translator.service.orchestrator import TranslationOrchestrator
from latin_translator.models import TranslationStages
import os
import logging
import sys

def verify_is_english(text, logger=None):
    """Verify that text is in English rather than Latin.
    
    Args:
        text: The text to check
        logger: Optional logger to log details
        
    Returns:
        True if the text appears to be in English
        
    Raises:
        AssertionError if the text doesn't appear to be in English
    """
    # Check for English articles and common function words
    english_common_words = ['the', 'and', 'is', 'are', 'to', 'of', 'that', 'in', 'you', 'your']
    english_word_count = sum(1 for word in english_common_words if word.lower() in text.lower().split())
    
    # Assert with informative message
    assert english_word_count >= 2, f"Translation doesn't appear to be in English (found only {english_word_count} English markers)"
    
    if logger:
        logger.info(f"Verified text is English (found {english_word_count} English markers)")
    
    return True

@pytest.mark.integration
def test_full_translation_flow(tmp_path, capsys):
    """Test the full flow from loading mock letters through translation."""
    # Set up logging
    logger = logging.getLogger(__name__)
    
    # Skip if no OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set, skipping test")
        pytest.skip("OPENAI_API_KEY not set")
    
    logger.info("Starting integration test with mock letters")
    
    # Initialize services using default test data directory
    letter_source = MockLetterSource()
    orchestrator = TranslationOrchestrator()
    translation_service = TranslationService(orchestrator)
    logger.info("Initialized letter source and translation service")
    
    # Load and translate both letters
    logger.info("Loading letters from mock source")
    letters = letter_source.fetch_all_letters()
    assert len(letters) == 2
    logger.info(f"Successfully loaded {len(letters)} letters")
    
    # Verify first letter
    letter1 = letters[0]
    assert letter1.title == "SENECA LUCILIO SUO SALUTEM"
    assert letter1.roman == "I"
    assert letter1.number == 1
    logger.info(f"Verified letter 1: {letter1.roman}. {letter1.title}")
    
    # Translate first letter
    logger.info("Starting translation of first letter")
    translation1 = translation_service.translate_letter(letter1)
    assert len(translation1) == 1  # One paragraph
    assert all(isinstance(para, TranslationStages) for para in translation1)
    assert all(len(para.original) > 0 for para in translation1)
    assert all(len(para.direct) > 0 for para in translation1)
    assert all(len(para.rhetorical) > 0 for para in translation1)
    logger.info(f"Successfully translated letter 1 ({len(translation1)} paragraphs)")
    
    # Log sample of first translation
    translated_text1 = "\n\n".join([" ".join(para.rhetorical) for para in translation1])
    logger.info("Sample of letter 1 translation:")
    logger.info(translated_text1[:200] + "..." if len(translated_text1) > 200 else translated_text1)
    
    # Verify translation is in English
    verify_is_english(translated_text1, logger)
    
    # Verify second letter
    letter2 = letters[1]
    assert letter2.title == "SENECA LUCILIO SUO SALUTEM"
    assert letter2.roman == "II"
    assert letter2.number == 2
    logger.info(f"Verified letter 2: {letter2.roman}. {letter2.title}")
    
    # Translate second letter
    logger.info("Starting translation of second letter")
    translation2 = translation_service.translate_letter(letter2)
    assert len(translation2) == 1  # One paragraph
    assert all(isinstance(para, TranslationStages) for para in translation2)
    assert all(len(para.original) > 0 for para in translation2)
    assert all(len(para.direct) > 0 for para in translation2)
    assert all(len(para.rhetorical) > 0 for para in translation2)
    logger.info(f"Successfully translated letter 2 ({len(translation2)} paragraphs)")
    
    # Log sample of second translation
    translated_text2 = "\n\n".join([" ".join(para.rhetorical) for para in translation2])
    logger.info("Sample of letter 2 translation:")
    logger.info(translated_text2[:200] + "..." if len(translated_text2) > 200 else translated_text2)
    
    # Verify translation is in English
    verify_is_english(translated_text2, logger)
    
    # Verify translations are different
    assert translated_text1 != translated_text2
    
    logger.info("Integration test completed successfully")

@pytest.mark.integration
def test_single_letter_translation():
    """Test translating a single letter."""
    # Set up logging
    logger = logging.getLogger(__name__)
    
    # Skip if no OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set, skipping test")
        pytest.skip("OPENAI_API_KEY not set")
    
    logger.info("Starting single letter translation test")
    
    # Initialize services
    letter_source = MockLetterSource()
    orchestrator = TranslationOrchestrator()
    translation_service = TranslationService(orchestrator)
    logger.info("Initialized letter source and translation service")
    
    # Load letter_1_head.txt directly
    letter1 = letter_source.fetch_letter("letter_1_head")
    assert letter1 is not None
    assert letter1.title == "SENECA LUCILIO SUO SALUTEM"
    assert letter1.roman == "I"
    assert letter1.number == 1
    logger.info(f"Successfully loaded letter: {letter1.roman}. {letter1.title}")
    
    # Log the Latin content
    logger.info(f"Latin content: {letter1.content[:100]}...")
    
    # Translate the letter
    logger.info("Starting translation")
    translation = translation_service.translate_letter(letter1)
    assert translation is not None
    assert len(translation) > 0
    assert all(isinstance(para, TranslationStages) for para in translation)
    assert all(len(para.original) > 0 for para in translation)
    assert all(len(para.direct) > 0 for para in translation)
    assert all(len(para.rhetorical) > 0 for para in translation)
    
    # Log the translation result
    translated_text = "\n\n".join([" ".join(para.rhetorical) for para in translation])
    logger.info("English translation:")
    logger.info(translated_text)
    
    # Verify that translation is in English
    verify_is_english(translated_text, logger)
    
    logger.info("Single letter translation test completed successfully") 