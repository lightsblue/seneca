import pytest
from pydantic import ValidationError
from latin_translator.models import Letter
from unittest.mock import patch, call
from latin_translator.models import TranslationStages


def test_letter_model():
    letter = Letter(number=1, roman="I", title="Test Title", content="Lorem ipsum dolor sit amet.")
    assert letter.number == 1
    assert letter.roman == "I"
    assert letter.title == "Test Title"
    assert letter.content == "Lorem ipsum dolor sit amet."


def test_invalid_letter_model():
    with pytest.raises(ValidationError):
        Letter(number="one", roman="I", title="Test Title", content="Lorem ipsum dolor sit amet.") 


def test_translation_stages_display():
    translation_stage = TranslationStages(
        paragraph_index=1,
        original=["Original Latin sentence 1.", "Original Latin sentence 2."],
        direct=["Direct translation 1.", "Direct translation 2."],
        rhetorical=["Final translation 1.", "Final translation 2."]
    )
    
    # Patch the built-in print function
    with patch('builtins.print') as mock_print:
        translation_stage.display()
        
        # Assert that print is called the correct number of times
        # 1 header + 2 sentences * 4 lines/sentence + 1 trailing newline = 10
        assert mock_print.call_count == 10

        # Check the specific calls
        expected_calls = [
            call("Paragraph 1"),
            call("\nSentence 1"),
            call("Original Latin:\n> Original Latin sentence 1."),
            call("Direct Translation:\n> Direct translation 1."),
            call("Final Translation:\n> Final translation 1."),
            call("\nSentence 2"),
            call("Original Latin:\n> Original Latin sentence 2."),
            call("Direct Translation:\n> Direct translation 2."),
            call("Final Translation:\n> Final translation 2."),
            call() # Trailing newline
        ]
        mock_print.assert_has_calls(expected_calls, any_order=False)

def test_translation_stages_display_many():
    translation_stage1 = TranslationStages(
        paragraph_index=1,
        original=["Original Latin sentence 1."],
        direct=["Direct translation 1."],
        rhetorical=["Final translation 1."]
    )
    translation_stage2 = TranslationStages(
        paragraph_index=2,
        original=["Original Latin sentence 2."],
        direct=["Direct translation 2."],
        rhetorical=["Final translation 2."]
    )
    stages = [translation_stage1, translation_stage2]
    
    # Patch the built-in print function
    with patch('builtins.print') as mock_print:
        TranslationStages.display_many(stages)
        
        # Assert that print is called the correct number of times
        # 2 paragraphs * (1 header + 1 sentence * 4 lines/sentence + 1 trailing newline) = 2 * 6 = 12
        assert mock_print.call_count == 12 