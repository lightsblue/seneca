import pytest
from unittest.mock import Mock
from latin_translator.models import Letter
from latin_translator.service.orchestrator import TranslationOrchestrator


def test_process_letter():
    mock_provider = Mock()
    mock_provider.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Translated sentence."))]
    )
    orchestrator = TranslationOrchestrator(provider=mock_provider)

    letter = Letter(number=1, roman="I", title="Test Title", content="Lorem ipsum dolor sit amet.")

    result = orchestrator.process_letter(letter)

    assert len(result) == 1
    assert result[0]["paragraph_index"] == 1
    assert result[0]["sentences"] == ["Translated sentence."]
    mock_provider.chat.completions.create.assert_called_once() 