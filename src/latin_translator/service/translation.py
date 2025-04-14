from typing import List
from ..models import Letter, TranslationRequest, ParagraphData
from .orchestrator import TranslationOrchestrator

class TranslationService:
    def __init__(self, orchestrator: TranslationOrchestrator):
        self.orchestrator = orchestrator

    def translate_letter(self, letter: Letter, request: TranslationRequest) -> List[ParagraphData]:
        return self.orchestrator.process_letter(letter, request) 