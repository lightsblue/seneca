import pytest
from unittest.mock import patch, MagicMock
from latin_translator.models import Letter
from latin_translator.service.seneca_letter_downloader import SenecaLetterDownloader

# Sample HTML content snippets for testing extract_letters
SAMPLE_HTML_ONE_LETTER = """
<html><body>
<p><b>I. SENECA LVCILIO SVO SALVTEM</b></p>
<p>[1] Ita fac, mi Lucili: vindica te tibi, et tempus quod adhuc aut auferebatur aut subripiebatur aut excidebat collige et serva.</p>
<p>[2] Persuade tibi hoc sic esse ut scribo: quaedam tempora eripiuntur nobis, quaedam subducuntur, quaedam effluunt.</p>
<p class="shortborder"> </p> <!-- Simulate end border -->
</body></html>
"""

SAMPLE_HTML_TWO_LETTERS = """
<html><body>
<p><b>I. SENECA LVCILIO SVO SALVTEM</b></p>
<p>[1] First section of Letter 1.</p>
<p>[2] Second section of Letter 1.</p>
<p><b>II. ALTER SENECA LVCILIO SVO SALVTEM</b></p>
<p>[1] First section of Letter 2.</p>
<p class="shortborder"> </p>
</body></html>
"""

SAMPLE_HTML_NO_MARKERS = """
<html><body>
<p><b>III. TITLE ONLY</b></p>
<p>Some content without section markers.</p>
<p class="shortborder"> </p>
</body></html>
"""

# --- Tests for _parse_sections ---

def test_parse_sections_basic():
    content = "[1] Section one.\n[2] Section two with\nnewline."
    expected = {
        1: "[1] Section one.\n",
        2: "[2] Section two with\nnewline."
    }
    assert SenecaLetterDownloader._parse_sections(content) == expected

def test_parse_sections_leading_text_ignored():
    content = "Ignore this. [1] Section one."
    expected = {1: "[1] Section one."}
    # Text before the first marker should currently be ignored by the parsing logic
    assert SenecaLetterDownloader._parse_sections(content) == expected

def test_parse_sections_trailing_whitespace():
    content = "[1] Section one.  \n[2] Section two. "
    expected = {
        1: "[1] Section one.  \n",
        2: "[2] Section two. "
    }
    assert SenecaLetterDownloader._parse_sections(content) == expected

def test_parse_sections_no_markers():
    content = "Just some plain text."
    expected = {}
    assert SenecaLetterDownloader._parse_sections(content) == expected

def test_parse_sections_single_section():
    content = "[5] Only one section here."
    expected = {5: "[5] Only one section here."}
    assert SenecaLetterDownloader._parse_sections(content) == expected

# --- Tests for extract_letters ---

def test_extract_letters_one_letter():
    letters = SenecaLetterDownloader.extract_letters(SAMPLE_HTML_ONE_LETTER)
    assert len(letters) == 1
    letter = letters[0]
    assert letter.number == 1
    assert letter.roman == "I"
    assert letter.title == "SENECA LVCILIO SVO SALVTEM"
    assert letter.content == "[1] Ita fac, mi Lucili: vindica te tibi, et tempus quod adhuc aut auferebatur aut subripiebatur aut excidebat collige et serva.\n[2] Persuade tibi hoc sic esse ut scribo: quaedam tempora eripiuntur nobis, quaedam subducuntur, quaedam effluunt."
    assert 1 in letter.sections
    assert 2 in letter.sections
    assert letter.sections[1] == "[1] Ita fac, mi Lucili: vindica te tibi, et tempus quod adhuc aut auferebatur aut subripiebatur aut excidebat collige et serva.\n"
    assert letter.sections[2].startswith("[2] Persuade tibi hoc sic esse ut scribo:") # Check start

def test_extract_letters_two_letters():
    letters = SenecaLetterDownloader.extract_letters(SAMPLE_HTML_TWO_LETTERS)
    assert len(letters) == 2

    # Letter 1
    l1 = letters[0]
    assert l1.number == 1
    assert l1.content == "[1] First section of Letter 1.\n[2] Second section of Letter 1."
    assert l1.sections == {
        1: "[1] First section of Letter 1.\n",
        2: "[2] Second section of Letter 1."
    }

    # Letter 2
    l2 = letters[1]
    assert l2.number == 2
    assert l2.content == "[1] First section of Letter 2."
    assert l2.sections == {1: "[1] First section of Letter 2."}


def test_extract_letters_no_markers():
    letters = SenecaLetterDownloader.extract_letters(SAMPLE_HTML_NO_MARKERS)
    assert len(letters) == 1
    letter = letters[0]
    assert letter.number == 3
    assert letter.title == "TITLE ONLY"
    assert letter.content == "Some content without section markers."
    assert letter.sections == {} # Expect empty sections dict

# --- Tests for get_letter_by_number ---

@pytest.fixture
def downloader():
    # Patch fetch_all_letters to avoid actual HTTP requests during tests
    with patch.object(SenecaLetterDownloader, 'fetch_all_letters') as mock_fetch:
        downloader_instance = SenecaLetterDownloader(urls=["dummy"]) # URL doesn't matter due to patch
        # Sample letters for the index
        mock_letters = [
            Letter(number=1, roman="I", title="T1", content="[1] C1", sections={1: "[1] C1"}),
            Letter(number=5, roman="V", title="T5", content="[1] C5", sections={1: "[1] C5"}),
        ]
        # Configure the mock to return the sample letters AND populate the internal index
        def side_effect_fetch():
            downloader_instance._letters_by_number = {l.number: l for l in mock_letters}
            return mock_letters
        mock_fetch.side_effect = side_effect_fetch

        yield downloader_instance # Provide the patched instance to tests

def test_get_letter_by_number_exists(downloader):
    # Fetch needs to be called once to populate index via side effect
    downloader.fetch_all_letters()
    letter = downloader.get_letter_by_number(5)
    assert letter is not None
    assert letter.number == 5
    assert letter.roman == "V"

def test_get_letter_by_number_not_exists(downloader):
    downloader.fetch_all_letters() # Populate index
    letter = downloader.get_letter_by_number(99)
    assert letter is None

def test_get_letter_by_number_fetches_if_needed(downloader):
     # Access the mock directly from the patched object if needed
    mock_fetch = SenecaLetterDownloader.fetch_all_letters

    # Don't call fetch_all_letters explicitly, let get_letter_by_number trigger it
    assert not downloader._letters_by_number # Index should be empty initially
    letter = downloader.get_letter_by_number(1)
    assert letter is not None
    assert letter.number == 1
    mock_fetch.assert_called_once() # Verify fetch was called implicitly
    assert downloader._letters_by_number # Index should now be populated 