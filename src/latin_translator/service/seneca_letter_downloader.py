from typing import List, Optional, Dict
import requests
from bs4 import BeautifulSoup
import logging
import re
from ..models import Letter

logger = logging.getLogger(__name__)

class SenecaLetterDownloader:
    DEFAULT_URLS = [
        "https://www.thelatinlibrary.com/sen/seneca.ep1.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep2.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep3.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep4.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep5.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep6.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep7.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep8.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep9.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep10.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep11-13.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep14-15.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep17-18.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep19.shtml",
        "https://www.thelatinlibrary.com/sen/seneca.ep20.shtml"
    ]

    def __init__(self, urls: Optional[List[str]] = None):
        self.urls = urls if urls is not None else self.DEFAULT_URLS
        self._letters_by_number: Dict[int, Letter] = {}

    def fetch_all_letters(self) -> List[Letter]:
        """Download and extract all of Seneca's letters from the configured URLs."""
        all_letters: List[Letter] = []
        self._letters_by_number = {}
        for url in self.urls:
            logger.info(f"Processing {url}")
            try:
                content = self.download_content(url)
                letters = self.extract_letters(content)
                all_letters.extend(letters)
            except Exception as e:
                logger.error(f"An error occurred while processing {url}: {e}")

        for letter in all_letters:
            self._letters_by_number[letter.number] = letter

        return all_letters

    def get_letter_by_number(self, number: int) -> Optional[Letter]:
        """Retrieve a letter by its number. Returns None if not found."""
        if not self._letters_by_number:
            logger.info("Letter index is empty. Fetching all letters first.")
            self.fetch_all_letters()
        return self._letters_by_number.get(number)

    def fetch_letters_from_url(self, url: str) -> List[Letter]:
        """Download and extract Seneca's letters from a single URL."""
        content = self.download_content(url)
        return self.extract_letters(content)

    @staticmethod
    def download_content(url: str) -> str:
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    @staticmethod
    def roman_to_int(roman: str) -> int:
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

    @staticmethod
    def _parse_sections(content: str) -> Dict[int, str]:
        """Parse content into sections based on [n] markers."""
        sections = {}
        # Split by '[num]' but keep the delimiter. Capture group does this.
        parts = re.split(r'(\[\d+\])', content)

        # Handle potential empty string at the beginning if content starts with a marker
        if parts and parts[0] == '':
            parts = parts[1:]

        current_section_num = None
        current_section_content = []

        for part in parts:
            match = re.match(r'\[(\d+)\]', part)
            if match:
                # Found a section marker. Store the previous section if exists.
                if current_section_num is not None:
                    sections[current_section_num] = "".join(current_section_content)
                
                # Start the new section
                current_section_num = int(match.group(1))
                current_section_content = [part] # Include the marker itself
            elif current_section_num is not None:
                # Append text part to the current section
                current_section_content.append(part)
            # Ignore text before the first marker, if any

        # Store the last parsed section
        if current_section_num is not None:
            sections[current_section_num] = "".join(current_section_content)

        return sections

    @classmethod
    def extract_letters(cls, content: str) -> List[Letter]:
        soup = BeautifulSoup(content, 'html.parser')
        body = soup.find('body')
        letters: List[Letter] = []
        current_letter_number = None
        current_letter_roman = None
        current_letter_title = None
        current_letter_content_parts: List[str] = [] # Changed name for clarity
        collecting = False

        for tag in body.find_all('p'):
            b_tag = tag.find('b')
            if b_tag:
                # If we were collecting a previous letter, finalize and add it
                if current_letter_number is not None:
                    full_content = '\n'.join(current_letter_content_parts).strip()
                    parsed_sections = cls._parse_sections(full_content)
                    letters.append(Letter(
                        number=current_letter_number,
                        roman=current_letter_roman,
                        title=current_letter_title or "",
                        content=full_content,
                        sections=parsed_sections # Pass parsed sections
                    ))

                # Start processing the new letter found
                title_text = b_tag.get_text(strip=True)
                parts = title_text.split('.', 1)
                if len(parts) == 2:
                    roman_part = parts[0].strip()
                    try:
                        number = cls.roman_to_int(roman_part)
                        title_remainder = parts[1].strip()
                        current_letter_number = number
                        current_letter_roman = roman_part
                        current_letter_title = title_remainder
                        current_letter_content_parts = [] # Reset content parts
                        collecting = True
                    except ValueError:
                        # Handle cases where the bold text is not a valid letter start
                        collecting = False
                        current_letter_number = None
                        current_letter_title = None
                else:
                    # Title format doesn't match expected pattern
                    collecting = False
            elif tag.get('class') and 'shortborder' in tag.get('class'):
                # End of a letter indicated by a border
                if current_letter_number is not None:
                    full_content = '\n'.join(current_letter_content_parts).strip()
                    parsed_sections = cls._parse_sections(full_content)
                    letters.append(Letter(
                        number=current_letter_number,
                        roman=current_letter_roman,
                        title=current_letter_title or "",
                        content=full_content,
                        sections=parsed_sections # Pass parsed sections
                    ))
                # Reset state after the border
                current_letter_number = None
                current_letter_title = None
                current_letter_content_parts = []
                collecting = False
            elif collecting:
                # Append the text content of the paragraph
                current_letter_content_parts.append(tag.get_text())

        # Add the last letter if one was being processed
        if current_letter_number is not None and current_letter_content_parts:
            full_content = '\n'.join(current_letter_content_parts).strip()
            parsed_sections = cls._parse_sections(full_content)
            letters.append(Letter(
                number=current_letter_number,
                roman=current_letter_roman,
                title=current_letter_title or "",
                content=full_content,
                sections=parsed_sections # Pass parsed sections
            ))

        return letters

# Deprecated: use SenecaLetterDownloader instead
def fetch_letters(urls: List[str]) -> List[Letter]:
    """Deprecated: use SenecaLetterDownloader instead."""
    return SenecaLetterDownloader(urls).fetch_all_letters()