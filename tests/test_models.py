import pytest
from pydantic import ValidationError
from latin_translator.models import Letter, TranslationRequest, ParagraphData


def test_letter_model():
    letter = Letter(number=1, roman="I", title="Test Title", content="Lorem ipsum dolor sit amet.")
    assert letter.number == 1
    assert letter.roman == "I"
    assert letter.title == "Test Title"
    assert letter.content == "Lorem ipsum dolor sit amet."


def test_translation_request_model():
    request = TranslationRequest(text="Lorem ipsum dolor sit amet.", instructions="Translate this text.")
    assert request.text == "Lorem ipsum dolor sit amet."
    assert request.instructions == "Translate this text."
    assert request.max_context == 1
    assert request.translate is True
    assert request.monologue_threshold == 3


def test_paragraph_data_model():
    paragraph_data = ParagraphData(paragraph_index=1, sentences=["Sentence 1.", "Sentence 2."])
    assert paragraph_data.paragraph_index == 1
    assert paragraph_data.sentences == ["Sentence 1.", "Sentence 2."]


def test_invalid_letter_model():
    with pytest.raises(ValidationError):
        Letter(number="one", roman="I", title="Test Title", content="Lorem ipsum dolor sit amet.") 