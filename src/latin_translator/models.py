from typing import List, Optional
from pydantic import BaseModel

class Letter(BaseModel):
    """A letter from Seneca's collection."""
    number: int
    roman: str
    title: str
    content: str

class TranslationStages(BaseModel):
    """Represents the three stages of translation for a paragraph."""
    paragraph_index: int
    original: List[str]  # Original Latin sentences
    direct: List[str]    # Direct, literal translation
    rhetorical: List[str]  # Final rhetorical translation

    def display(self) -> None:
        """
        Display all stages of translation for this paragraph in a clear, formatted way using print.
        """
        print(f"Paragraph {self.paragraph_index}")
        for i, (orig, direct, rhet) in enumerate(zip(self.original, self.direct, self.rhetorical)):
            print(f"\nSentence {i+1}")
            print(f"Original Latin:\n> {orig}")
            print(f"Direct Translation:\n> {direct}")
            print(f"Final Translation:\n> {rhet}")
        print() # Add a blank line after each paragraph display

    @staticmethod
    def display_many(stages: List["TranslationStages"]) -> None:
        """
        Display all stages of translation for a list of paragraphs using print.
        """
        for stage in stages:
            stage.display() 