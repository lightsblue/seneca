import pytest
from pydantic import ValidationError
from latin_translator.models import Letter, ParagraphData


def test_letter_model():
    letter = Letter(number=1, roman="I", title="Test Title", content="Lorem ipsum dolor sit amet.")
    assert letter.number == 1
    assert letter.roman == "I"
    assert letter.title == "Test Title"
    assert letter.content == "Lorem ipsum dolor sit amet."


def test_paragraph_data_model():
    paragraph = ParagraphData(paragraph_index=1, sentences=["First sentence.", "Second sentence."])
    assert paragraph.paragraph_index == 1
    assert len(paragraph.sentences) == 2
    assert paragraph.sentences[0] == "First sentence."
    assert paragraph.sentences[1] == "Second sentence."


def test_invalid_letter_model():
    with pytest.raises(ValidationError):
        Letter(number="one", roman="I", title="Test Title", content="Lorem ipsum dolor sit amet.") 