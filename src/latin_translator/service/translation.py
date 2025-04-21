from typing import List
from ..models import Letter, TranslationStages
from .orchestrator import TranslationOrchestrator

class TranslationService:
    def __init__(self, orchestrator: TranslationOrchestrator):
        self.orchestrator = orchestrator

    def translate_letter(self, letter: Letter) -> List[TranslationStages]:
        """
        Translate a letter and return all stages of translation.
        
        Args:
            letter: The letter to translate
            
        Returns:
            List of TranslationStages containing original, direct, and rhetorical translations
        """
        return self.orchestrator.process_letter(letter)