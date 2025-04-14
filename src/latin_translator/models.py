from typing import List
from pydantic import BaseModel

class Letter(BaseModel):
    number: int
    roman: str
    title: str
    content: str

class TranslationRequest(BaseModel):
    text: str
    instructions: str
    max_context: int = 1
    translate: bool = True
    monologue_threshold: int = 3

class ParagraphData(BaseModel):
    paragraph_index: int
    sentences: List[str] 