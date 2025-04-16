from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from ..models import Letter

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

    def fetch_all_letters(self) -> List[Letter]:
        """Download and extract all of Seneca's letters from the configured URLs."""
        all_letters: List[Letter] = []
        for url in self.urls:
            print(f"Processing {url}")
            try:
                content = self.download_content(url)
                letters = self.extract_letters(content)
                all_letters.extend(letters)
            except Exception as e:
                print(f"An error occurred while processing {url}: {e}")
        return all_letters

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

    @classmethod
    def extract_letters(cls, content: str) -> List[Letter]:
        soup = BeautifulSoup(content, 'html.parser')
        body = soup.find('body')
        letters: List[Letter] = []
        current_letter_number = None
        current_letter_roman = None
        current_letter_title = None
        current_letter_content: List[str] = []
        collecting = False

        for tag in body.find_all('p'):
            b_tag = tag.find('b')
            if b_tag:
                if current_letter_number is not None:
                    letters.append(Letter(
                        number=current_letter_number,
                        roman=current_letter_roman,
                        title=current_letter_title or "",
                        content='\n'.join(current_letter_content).strip()
                    ))

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
                        current_letter_content = []
                        collecting = True
                    except ValueError:
                        collecting = False
                        current_letter_number = None
                        current_letter_title = None
                else:
                    collecting = False
            elif tag.get('class') and 'shortborder' in tag.get('class'):
                if current_letter_number is not None:
                    letters.append(Letter(
                        number=current_letter_number,
                        roman=current_letter_roman,
                        title=current_letter_title or "",
                        content='\n'.join(current_letter_content).strip()
                    ))
                current_letter_number = None
                current_letter_title = None
                current_letter_content = []
                collecting = False
            elif collecting:
                current_letter_content.append(tag.get_text())

        if current_letter_number is not None and current_letter_content:
            letters.append(Letter(
                number=current_letter_number,
                roman=current_letter_roman,
                title=current_letter_title or "",
                content='\n'.join(current_letter_content).strip()
            ))

        return letters

# Deprecated: use SenecaLetterDownloader instead
def fetch_letters(urls: List[str]) -> List[Letter]:
    """Deprecated: use SenecaLetterDownloader instead."""
    return SenecaLetterDownloader(urls).fetch_all_letters()