import pytest
from unittest.mock import Mock
from latin_translator.models import Letter
from latin_translator.service.batch import BatchProcessor
from latin_translator.service.letter_translator import LetterTranslator


def test_process_letters():
    # Create a mock orchestrator
    mock_orchestrator = Mock()
    mock_orchestrator.process_letter.return_value = [
        {"paragraph_index": 1, "sentences": ["Translated sentence 1."]}
    ]
    
    batch_processor = BatchProcessor(orchestrator=mock_orchestrator)
    
    # Create test letters
    letters = [
        Letter(number=1, roman="I", title="Test 1", content="Lorem ipsum."),
        Letter(number=2, roman="II", title="Test 2", content="Dolor sit amet.")
    ]
    
    # Process the letters
    results = batch_processor.process_letters(letters)
    
    # Verify results
    assert len(results) == 2
    assert results[0] == mock_orchestrator.process_letter.return_value
    assert results[1] == mock_orchestrator.process_letter.return_value
    
    # Verify the orchestrator was called correctly for each letter
    assert mock_orchestrator.process_letter.call_count == 2
    mock_orchestrator.process_letter.assert_any_call(letters[0])
    mock_orchestrator.process_letter.assert_any_call(letters[1]) 