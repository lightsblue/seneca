from typing import List
from ..models import Letter, ParagraphData
from .orchestrator import TranslationOrchestrator

class BatchProcessor:
    def __init__(self, orchestrator: TranslationOrchestrator):
        self.orchestrator = orchestrator

    def process_letters(self, letters: List[Letter]) -> List[List[ParagraphData]]:
        all_translations = []
        for letter in letters:
            translation = self.orchestrator.process_letter(letter)
            all_translations.append(translation)
        return all_translations 