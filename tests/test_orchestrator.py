import pytest
from unittest.mock import Mock, patch
from latin_translator.models import Letter, TranslationStages
from latin_translator.service.letter_translator import LetterTranslator


def test_process_letter():
    mock_completion = Mock()
    mock_completion.choices = [Mock(message=Mock(content="Translated sentence."))]
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_completion

    with patch("latin_translator.service.letter_translator.OpenAI", return_value=mock_client):
        translator = LetterTranslator()
        
        # Test with string content
        text_content = "Lorem ipsum dolor sit amet."
        result = translator.process_letter(text_content)

        assert len(result) == 1
        assert isinstance(result[0], TranslationStages)
        assert result[0].paragraph_index == 1
        assert result[0].original == ["Lorem ipsum dolor sit amet."]
        assert result[0].direct == ["Translated sentence."]
        assert result[0].rhetorical == ["Translated sentence."]
        assert mock_client.chat.completions.create.call_count == 2  # Once for direct, once for rhetorical