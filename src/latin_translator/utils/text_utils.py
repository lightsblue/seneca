from typing import List
import re


def split_paragraphs(text: str) -> List[str]:
    """Split the text on double newlines into paragraphs."""
    return [p.strip() for p in text.strip().split('\n\n') if p.strip()]


def split_text_with_quotes(text: str) -> List[str]:
    """
    Split text on sentence-ending punctuation, but preserve everything
    within matching single or double quotes as a single chunk.
    """
    chunks = []
    current_chunk = []
    inside_quotes = False
    quote_char = None  # Tracks whether we opened a single/double quote

    for char in text:
        current_chunk.append(char)
        # Toggle quotes if encountering any quote characters.
        if char in ['"', '“', '”']:
            if not inside_quotes:
                inside_quotes = True
                quote_char = char
            else:
                if char == quote_char:
                    inside_quotes = False
                    quote_char = None
        # If we're not inside quotes, treat '.', '!', '?' as sentence boundaries.
        if not inside_quotes and char in ['.', '!', '?']:
            chunks.append(''.join(current_chunk).strip())
            current_chunk = []
        # Continue adding characters to the current chunk if inside quotes
        else:
            continue
    if current_chunk:
        leftover = ''.join(current_chunk).strip()
        if leftover:
            chunks.append(leftover)
    return chunks


def split_naive_sentences(text: str) -> List[str]:
    """A simple sentence splitter that always splits on '.', '!', or '?'."""
    chunks = []
    current_chunk = []
    for char in text:
        current_chunk.append(char)
        if char in ['.', '!', '?']:
            chunks.append(''.join(current_chunk).strip())
            current_chunk = []
    if current_chunk:
        leftover = ''.join(current_chunk).strip()
        if leftover:
            chunks.append(leftover)
    return chunks


def extract_outer_quoted_parts(text: str) -> tuple:
    """
    If text contains at least one pair of matching quotes (either ' or "),
    extract and return a tuple of (prefix, quote_char, inner_text, suffix).
    For example, given:
       "Clamo: 'Avoid the crowd. Stay away.' Extra text"
    it returns:
       ("Clamo: ", "'", "Avoid the crowd. Stay away.", " Extra text")
    If no matching quotes are found, returns ("", None, text, "").
    """
    first_quote = re.search(r"['\"]", text)
    if first_quote:
        quote_char = text[first_quote.start()]
        last_quote = text.rfind(quote_char)
        if last_quote > first_quote.start():
            prefix = text[:first_quote.start()]
            inner = text[first_quote.start()+1:last_quote]
            suffix = text[last_quote+1:]
            return prefix, quote_char, inner, suffix
    return "", None, text, ""


def clean_translation(text: str, original_sentence: str = "") -> str:
    """
    Remove wrapping quotes added by the LLM, and optionally reattach any leading numbering.
    """
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()
    m = re.match(r'^(\[\d+\])', original_sentence)
    if m and not text.startswith(m.group(1)):
        text = m.group(1) + " " + text
    return text 