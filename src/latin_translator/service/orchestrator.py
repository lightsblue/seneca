from typing import List, Optional
import os
from openai import OpenAI
from ..models import Letter, ParagraphData
from ..text.utils import split_paragraphs, split_text_with_quotes, clean_translation

class TranslationOrchestrator:
    """
    Coordinates the translation process using AI providers and text processing utilities.
    Follows the two-phase translation approach:
    1. Direct, literal translation preserving Latin structure
    2. Rhetorical rewrite for modern clarity while maintaining philosophical precision
    """

    def __init__(self, model: str = "gpt-4", max_context: int = 2):
        """
        Initialize the orchestrator with configuration.

        Args:
            model: The OpenAI model to use for translation
            max_context: Number of previous exchanges to include for context
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.max_context = max_context
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Load prompt templates from files."""
        base_path = os.path.dirname(os.path.dirname(__file__))
        prompt_path = os.path.join(base_path, "prompts")
        
        with open(os.path.join(prompt_path, "translate.v1.txt")) as f:
            self.direct_prompt = f.read()
        
        with open(os.path.join(prompt_path, "rewrite.v1.txt")) as f:
            self.rewrite_prompt = f.read()

    def translate_chunk(
        self,
        text: str,
        system_prompt: str,
        conversation_history: Optional[List[dict]] = None
    ) -> tuple[str, List[dict]]:
        """
        Translate a single chunk of text while maintaining conversation history.

        Args:
            text: The text to translate
            system_prompt: The system prompt to use
            conversation_history: Optional list of previous messages

        Returns:
            Tuple of (translation, updated conversation history)
        """
        if conversation_history is None:
            conversation_history = [{"role": "system", "content": system_prompt}]
        
        conversation_history.append({"role": "user", "content": text})
        
        # Keep only recent context
        if len(conversation_history) > (self.max_context * 2 + 1):
            messages = [conversation_history[0]] + conversation_history[-(self.max_context * 2):]
        else:
            messages = conversation_history

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        
        reply = completion.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": reply})
        
        return clean_translation(reply), conversation_history

    def translate_direct(self, text: str) -> str:
        """
        Perform the first-phase direct translation.

        Args:
            text: The Latin text to translate

        Returns:
            A literal English translation preserving Latin structure
        """
        paragraphs = split_paragraphs(text)
        translated_paragraphs = []
        conversation_history = None

        for paragraph in paragraphs:
            translated_sentences = []
            sentences = split_text_with_quotes(paragraph)
            
            for sentence in sentences:
                translation, conversation_history = self.translate_chunk(
                    sentence,
                    self.direct_prompt,
                    conversation_history
                )
                translated_sentences.append(translation)
            
            translated_paragraphs.append(" ".join(translated_sentences))
        
        return "\n\n".join(translated_paragraphs)

    def translate_rhetorical(self, text: str) -> str:
        """
        Perform the second-phase rhetorical translation.

        Args:
            text: The literal English translation to rewrite

        Returns:
            A clear, modern English translation
        """
        paragraphs = split_paragraphs(text)
        final_paragraphs = []
        conversation_history = None

        for paragraph in paragraphs:
            translation, conversation_history = self.translate_chunk(
                paragraph,
                self.rewrite_prompt,
                conversation_history
            )
            final_paragraphs.append(translation)
        
        return "\n\n".join(final_paragraphs)

    def process_letter(self, letter: Letter) -> List[ParagraphData]:
        """
        Process a complete letter through both translation phases.
        
        Args:
            letter: The letter to translate
            
        Returns:
            List of translated paragraphs with their sentences
        """
        # First phase: Direct translation
        direct_translation = self.translate_direct(letter.content)
        
        # Second phase: Rhetorical rewrite
        final_translation = self.translate_rhetorical(direct_translation)
        
        # Convert to paragraph data structure
        paragraphs = split_paragraphs(final_translation)
        result: List[ParagraphData] = []
        
        for idx, paragraph in enumerate(paragraphs, start=1):
            sentences = split_text_with_quotes(paragraph)
            result.append({
                "paragraph_index": idx,
                "sentences": sentences
            })
        
        return result 