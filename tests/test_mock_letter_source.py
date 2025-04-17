import pytest
from pathlib import Path
from latin_translator.utils.mock_letter_source import MockLetterSource
from latin_translator.models import Letter

def test_mock_letter_source_loads_letter(tmp_path):
    # Create a custom test data directory
    test_dir = tmp_path / "test_letters"
    test_dir.mkdir()
    
    # Create a test letter file with Roman numeral title
    letter_file = test_dir / "wisdom.txt"
    letter_file.write_text("I. The Nature of Wisdom\nWisdom is the art of living.")
    
    # Initialize mock letter source with custom directory
    letter_source = MockLetterSource(test_data_dir=test_dir)
    
    # Load letter by name
    letter = letter_source.fetch_letter("wisdom")
    
    assert letter is not None
    assert letter.title == "The Nature of Wisdom"
    assert letter.content == "Wisdom is the art of living."
    assert letter.number == 1
    assert letter.roman == "I"

def test_mock_letter_source_loads_all_letters(tmp_path):
    # Create a custom test data directory
    test_dir = tmp_path / "test_letters"
    test_dir.mkdir()
    
    # Create multiple test letters with Roman numerals
    (test_dir / "wisdom.txt").write_text("I. Wisdom\nContent about wisdom")
    (test_dir / "virtue.txt").write_text("II. Virtue\nContent about virtue")
    (test_dir / "courage.txt").write_text("III. Courage\nContent about courage")
    
    letter_source = MockLetterSource(test_data_dir=test_dir)
    letters = letter_source.fetch_all_letters()
    
    assert len(letters) == 3
    assert all(isinstance(letter, Letter) for letter in letters)
    
    # Letters should be numbered according to their Roman numerals
    letters_by_title = {letter.title: letter for letter in letters}
    assert letters_by_title["Wisdom"].number == 1
    assert letters_by_title["Virtue"].number == 2
    assert letters_by_title["Courage"].number == 3
    
def test_mock_letter_source_handles_missing_letter(tmp_path):
    letter_source = MockLetterSource(test_data_dir=tmp_path)
    assert letter_source.fetch_letter("nonexistent") is None

def test_mock_letter_source_handles_empty_file(tmp_path):
    test_dir = tmp_path / "test_letters"
    test_dir.mkdir()
    
    # Create an empty file
    (test_dir / "empty.txt").write_text("")
    
    letter_source = MockLetterSource(test_data_dir=test_dir)
    with pytest.raises(ValueError, match="Empty letter file"):
        letter_source.fetch_letter("empty")

def test_mock_letter_source_handles_invalid_title_format(tmp_path):
    test_dir = tmp_path / "test_letters"
    test_dir.mkdir()
    
    # Create a file with invalid title format (missing period after Roman numeral)
    (test_dir / "invalid.txt").write_text("I The Title\nSome content")
    
    letter_source = MockLetterSource(test_data_dir=test_dir)
    with pytest.raises(ValueError, match="Invalid title format"):
        letter_source.fetch_letter("invalid")

def test_mock_letter_source_handles_invalid_roman_numeral(tmp_path):
    test_dir = tmp_path / "test_letters"
    test_dir.mkdir()
    
    # Create a file with invalid Roman numeral
    (test_dir / "invalid.txt").write_text("ABC. The Title\nSome content")
    
    letter_source = MockLetterSource(test_data_dir=test_dir)
    with pytest.raises(ValueError, match="Invalid Roman numeral"):
        letter_source.fetch_letter("invalid") 