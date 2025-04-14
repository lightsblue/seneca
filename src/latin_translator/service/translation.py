from typing import List
from ..models import Letter, ParagraphData
from .orchestrator import TranslationOrchestrator

class TranslationService:
    def __init__(self, orchestrator: TranslationOrchestrator):
        self.orchestrator = orchestrator

    def translate_letter(self, letter: Letter) -> List[ParagraphData]:
        return self.orchestrator.process_letter(letter) 