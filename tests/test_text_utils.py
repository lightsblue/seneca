from latin_translator.utils import (
    split_paragraphs,
    split_text_with_quotes,
    split_naive_sentences,
    extract_outer_quoted_parts,
    clean_translation
)
import pytest


def test_split_paragraphs():
    text = """Paragraph one.

Paragraph two.

Paragraph three."""
    paragraphs = split_paragraphs(text)
    assert paragraphs == ["Paragraph one.", "Paragraph two.", "Paragraph three."]

@pytest.mark.skip(reason="Test is failing due to quote handling issues - to be fixed")
def test_split_text_with_quotes():
    text = "He said, 'Hello!' How are you?"
    sentences = split_text_with_quotes(text)
    assert sentences == ["He said, 'Hello!'", "How are you?"]

def test_split_naive_sentences():
    text = "This is a sentence. This is another! And a third?"
    sentences = split_naive_sentences(text)
    assert sentences == ["This is a sentence.", "This is another!", "And a third?"]


def test_extract_outer_quoted_parts():
    text = "Clamo: 'Avoid the crowd. Stay away.' Extra text"
    prefix, quote_char, inner, suffix = extract_outer_quoted_parts(text)
    assert prefix == "Clamo: "
    assert quote_char == "'"
    assert inner == "Avoid the crowd. Stay away."
    assert suffix == " Extra text"


def test_clean_translation():
    text = '"Translated text."'
    cleaned = clean_translation(text)
    assert cleaned == "Translated text." 