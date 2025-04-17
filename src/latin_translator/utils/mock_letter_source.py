from pathlib import Path
from typing import List, Optional
import logging
from ..models import Letter

logger = logging.getLogger(__name__)

class MockLetterSource:
    """A mock letter source that loads test letters from text files.
    
    This class provides a similar interface to SenecaLetterDownloader but loads letters
    from local text files instead of web URLs. It's designed for testing purposes.
    
    Text files should be placed in the tests/test_data/letters directory.
    Files should be named <name>.txt (e.g., letter_1_head.txt).
    
    The first line of each file should contain the title in the format:
    "I. TITLE" or "II. TITLE" etc., where the Roman numeral is followed by a period.
    The rest of the file contains the letter content.
    """
    
    DEFAULT_TEST_DATA_DIR = Path("tests/test_data/letters")
    
    def __init__(self, test_data_dir: Optional[Path] = None):
        """Initialize the mock letter source.
        
        Args:
            test_data_dir: Optional path to the directory containing test letter files.
                          If not provided, uses DEFAULT_TEST_DATA_DIR.
        """
        self.test_data_dir = test_data_dir or self.DEFAULT_TEST_DATA_DIR
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_all_letters(self) -> List[Letter]:
        """Load all test letters from the test data directory."""
        all_letters: List[Letter] = []
        
        for letter_file in sorted(self.test_data_dir.glob("*.txt")):
            try:
                letter = self._load_letter_from_file(letter_file)
                all_letters.append(letter)
            except Exception as e:
                logger.error(f"Error loading test letter from {letter_file}: {e}")
                
        return all_letters
    
    def fetch_letter(self, name: str) -> Optional[Letter]:
        """Load a specific test letter by name.
        
        Args:
            name: The name of the letter file (without .txt extension)
            
        Returns:
            The Letter object if found, None otherwise.
        """
        letter_path = self.test_data_dir / f"{name}.txt"
        if not letter_path.exists():
            return None
            
        return self._load_letter_from_file(letter_path)
    
    @staticmethod
    def _load_letter_from_file(file_path: Path) -> Letter:
        """Load a letter from a text file.
        
        The file format should be:
        First line: "I. TITLE" (Roman numeral followed by period and title)
        Rest of file: Content
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines:
            raise ValueError(f"Empty letter file: {file_path}")
            
        # Parse the title line to extract Roman numeral and title
        title_line = lines[0].strip()
        parts = title_line.split('.', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid title format in {file_path}. Expected 'ROMAN_NUMERAL. TITLE', got '{title_line}'")
            
        roman_part = parts[0].strip()
        title = parts[1].strip()
        
        try:
            number = MockLetterSource._roman_to_int(roman_part)
        except ValueError as e:
            raise ValueError(f"Invalid Roman numeral in title of {file_path}: {roman_part}") from e
            
        content = ''.join(lines[1:]).strip()
        
        return Letter(
            number=number,
            roman=roman_part,
            title=title,
            content=content
        )
    
    @staticmethod
    def _roman_to_int(roman: str) -> int:
        """Convert a Roman numeral to an integer.
        
        Args:
            roman: The Roman numeral string (e.g., 'I', 'IV', 'X')
            
        Returns:
            The integer value of the Roman numeral
            
        Raises:
            ValueError: If the string contains invalid Roman numeral characters
        """
        roman = roman.upper()
        roman_numerals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        result = 0
        prev_value = 0
        
        for c in reversed(roman):
            if c not in roman_numerals:
                raise ValueError(f"Invalid Roman numeral character: {c}")
            value = roman_numerals[c]
            if value < prev_value:
                result -= value
            else:
                result += value
                prev_value = value
        return result 