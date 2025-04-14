from typing import List, Optional
from pydantic import BaseModel

class Letter(BaseModel):
    """A letter from Seneca's collection."""
    number: int
    roman: str
    title: str
    content: str

class ParagraphData(BaseModel):
    """Structured data for a translated paragraph."""
    paragraph_index: int
    sentences: List[str] 