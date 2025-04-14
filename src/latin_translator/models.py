from typing import List, Optional
from pydantic import BaseModel

class Letter(BaseModel):
    """A letter from Seneca's collection."""
    number: int
    roman: str
    title: str
    content: str

class TranslationRequest(BaseModel):
    """Configuration for a translation request."""
    text: str
    instructions: Optional[str] = None
    max_context: int = 2
    translate: bool = True

class ParagraphData(BaseModel):
    """Structured data for a translated paragraph."""
    paragraph_index: int
    sentences: List[str] 