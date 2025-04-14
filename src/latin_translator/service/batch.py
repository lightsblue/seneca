from typing import List
from ..models import Letter, TranslationRequest, ParagraphData
from .orchestrator import TranslationOrchestrator

class BatchProcessor:
    def __init__(self, orchestrator: TranslationOrchestrator):
        self.orchestrator = orchestrator

    def process_letters(self, letters: List[Letter], request: TranslationRequest) -> List[List[ParagraphData]]:
        all_translations = []
        for letter in letters:
            translation = self.orchestrator.process_letter(letter, request)
            all_translations.append(translation)
        return all_translations 