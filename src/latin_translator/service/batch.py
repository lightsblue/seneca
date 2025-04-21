from typing import List
from ..models import Letter, TranslationStages
from .orchestrator import TranslationOrchestrator

class BatchProcessor:
    def __init__(self, orchestrator: TranslationOrchestrator):
        self.orchestrator = orchestrator

    def process_letters(self, letters: List[Letter]) -> List[List[TranslationStages]]:
        """
        Process multiple letters in batch.
        
        Args:
            letters: List of letters to translate
            
        Returns:
            List of translation stages for each letter
        """
        all_translations = []
        for letter in letters:
            translation = self.orchestrator.process_letter(letter)
            all_translations.append(translation)
        return all_translations 