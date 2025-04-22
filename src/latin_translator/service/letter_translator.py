from typing import List, Optional
import os
import logging
import json
from openai import OpenAI
import httpx
from ..models import Letter, TranslationStages
from ..utils import split_paragraphs, split_text_with_quotes, clean_translation

# Configure logging
# Removed basicConfig to use global configuration
logger = logging.getLogger(__name__)
http_logger = logging.getLogger(f"{__name__}.http")

# Define request and response hooks for logging
def log_request(request):
    method = request.method
    url = str(request.url)
    http_logger.debug(f"OpenAI Request: {method} {url}")
    
    # Log the request body
    if request.content:
        try:
            body = request.content.decode("utf-8")
            # Try to parse and pretty-print if it's JSON
            try:
                json_body = json.loads(body)
                http_logger.debug(f"Request body: {json.dumps(json_body, indent=2)}")
            except json.JSONDecodeError:
                http_logger.debug(f"Request body: {body}")
        except Exception as e:
            http_logger.debug(f"Could not decode request body: {e}")

def log_response(response):
    http_logger.debug(f"OpenAI Response: HTTP {response.status_code}")

class LetterTranslator:
    """
    Coordinates the translation process using AI providers and text processing utilities.
    Follows the two-phase translation approach:
    1. Direct, literal translation preserving Latin structure
    2. Rhetorical rewrite for modern clarity while maintaining philosophical precision
    """

    def __init__(self, model: str = "gpt-4o", max_context: int = 2):
        """
        Initialize the orchestrator with configuration.

        Args:
            model: The OpenAI model to use for translation
            max_context: Number of previous exchanges to include for context
        """
        # Create a client with our logging hooks
        event_hooks = {"request": [log_request], "response": [log_response]}
        http_client = httpx.Client(event_hooks=event_hooks)
        
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            http_client=http_client
        )
        
        self.model = model
        self.max_context = max_context
        self._load_prompts()
        logger.info(f"LetterTranslator initialized with model={model}, max_context={max_context}")

    def _load_prompts(self) -> None:
        """Load prompt templates from files."""
        base_path = os.path.dirname(os.path.dirname(__file__))
        prompt_path = os.path.join(base_path, "prompts")
        
        # Fix: These files were loaded with swapped names
        # direct.v1.txt contains the Latin->English translation prompt
        # rhetorical.v1.txt contains the English->Modern English prompt
        with open(os.path.join(prompt_path, "direct.v1.txt")) as f:
            self.direct_prompt = f.read()
        
        with open(os.path.join(prompt_path, "rhetorical.v1.txt")) as f:
            self.rhetorical_prompt = f.read()

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
        # Handle special case: lone quotation marks or very short (1-2 chars) input
        # Skip LLM call and preserve them exactly
        if len(text.strip()) <= 2 and all(char in "'\"" for char in text.strip()):
            logger.info(f"Detected lone quotation mark: '{text}'. Preserving as is.")
            if conversation_history is None:
                conversation_history = [{"role": "system", "content": system_prompt}]
            # Add a dummy exchange to maintain conversation structure
            conversation_history.append({"role": "user", "content": text})
            conversation_history.append({"role": "assistant", "content": text})
            return text, conversation_history
        
        if conversation_history is None:
            conversation_history = [{"role": "system", "content": system_prompt}]
        
        conversation_history.append({"role": "user", "content": text})
        
        # Keep only recent context
        if len(conversation_history) > (self.max_context * 2 + 1):
            messages = [conversation_history[0]] + conversation_history[-(self.max_context * 2):]
        else:
            messages = conversation_history

        logger.info(f"Making API request to {self.model} with {len(messages)} messages")
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            
            reply = completion.choices[0].message.content.strip()
            conversation_history.append({"role": "assistant", "content": reply})
            
            # Log the response body now that we've successfully used it
            if http_logger.isEnabledFor(logging.DEBUG):
                try:
                    http_logger.debug(f"Response content: {json.dumps(completion.model_dump(), indent=2)}")
                except Exception as e:
                    http_logger.debug(f"Could not log response content: {e}")
            
            logger.debug(f"API request completed, received {len(reply)} characters")
            return clean_translation(reply), conversation_history
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise

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
                self.rhetorical_prompt,
                conversation_history
            )
            final_paragraphs.append(translation)
        
        return "\n\n".join(final_paragraphs)

    def process_letter(self, content: str) -> List[TranslationStages]:
        """
        Process text through both translation phases.
        
        Args:
            content: The text content to translate
            
        Returns:
            List of TranslationStages containing original, direct, and rhetorical translations
        """
        # Split original text into paragraphs and sentences
        original_paragraphs = split_paragraphs(content)
        result: List[TranslationStages] = []
        
        for idx, original_paragraph in enumerate(original_paragraphs, start=1):
            # Split into sentences
            original_sentences = split_text_with_quotes(original_paragraph)
            
            # First phase: Direct translation
            direct_sentences = []
            conversation_history = None
            for sentence in original_sentences:
                translation, conversation_history = self.translate_chunk(
                    sentence,
                    self.direct_prompt,
                    conversation_history
                )
                direct_sentences.append(translation)
            
            # Second phase: Rhetorical translation
            rhetorical_sentences = []
            conversation_history = None
            for sentence in direct_sentences:
                translation, conversation_history = self.translate_chunk(
                    sentence,
                    self.rhetorical_prompt,
                    conversation_history
                )
                rhetorical_sentences.append(translation)
            
            # Create TranslationStages for this paragraph
            result.append(TranslationStages(
                paragraph_index=idx,
                original=original_sentences,
                direct=direct_sentences,
                rhetorical=rhetorical_sentences
            ))
        
        return result 