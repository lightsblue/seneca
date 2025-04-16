import pytest
from unittest.mock import Mock, patch
from latin_translator.models import Letter
from latin_translator.service.orchestrator import TranslationOrchestrator


def test_process_letter():
    mock_completion = Mock()
    mock_completion.choices = [Mock(message=Mock(content="Translated sentence."))]
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_completion

    with patch("latin_translator.service.orchestrator.OpenAI", return_value=mock_client):
        orchestrator = TranslationOrchestrator()
        letter = Letter(number=1, roman="I", title="Test Title", content="Lorem ipsum dolor sit amet.")
        result = orchestrator.process_letter(letter)

    assert len(result) == 1
    assert result[0]["paragraph_index"] == 1
    assert result[0]["sentences"] == ["Translated sentence."]
    mock_client.chat.completions.create.assert_called()