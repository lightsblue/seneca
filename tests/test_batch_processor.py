import pytest
from unittest.mock import Mock
from latin_translator.models import Letter, TranslationRequest
from latin_translator.service.batch import BatchProcessor
from latin_translator.service.orchestrator import TranslationOrchestrator


def test_process_letters():
    mock_orchestrator = Mock(spec=TranslationOrchestrator)
    mock_orchestrator.process_letter.return_value = [{
        "paragraph_index": 1,
        "sentences": ["Translated sentence."]
    }]
    batch_processor = BatchProcessor(orchestrator=mock_orchestrator)

    letters = [
        Letter(number=1, roman="I", title="Test Title 1", content="Lorem ipsum dolor sit amet."),
        Letter(number=2, roman="II", title="Test Title 2", content="Consectetur adipiscing elit.")
    ]
    request = TranslationRequest(text="", instructions="Translate this text.")

    result = batch_processor.process_letters(letters, request)

    assert len(result) == 2
    assert result[0][0]["paragraph_index"] == 1
    assert result[0][0]["sentences"] == ["Translated sentence."]
    assert result[1][0]["paragraph_index"] == 1
    assert result[1][0]["sentences"] == ["Translated sentence."]
    assert mock_orchestrator.process_letter.call_count == 2 