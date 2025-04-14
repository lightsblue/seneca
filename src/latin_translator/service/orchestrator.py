from typing import List
from ..models import Letter, TranslationRequest, ParagraphData
from ..text.utils import split_paragraphs, split_text_with_quotes, clean_translation

class TranslationOrchestrator:
    def __init__(self, provider):
        self.provider = provider

    def process_letter(self, letter: Letter, request: TranslationRequest) -> List[ParagraphData]:
        paragraphs = split_paragraphs(letter.content)
        output_paragraphs = []
        conversation_history = [{"role": "system", "content": request.instructions}] if request.translate and request.instructions else []

        for para_idx, paragraph in enumerate(paragraphs, start=1):
            sentence_list = []
            sentences = split_text_with_quotes(paragraph)
            for sentence in sentences:
                if request.translate:
                    prompt = f"Translate this sentence:\n\n{sentence}"
                    translation, conversation_history = self.translate_chunk(prompt, request, conversation_history)
                    translation = clean_translation(translation, original_sentence=sentence)
                else:
                    translation = sentence
                sentence_list.append(translation)
            output_paragraphs.append({
                "paragraph_index": para_idx,
                "sentences": sentence_list
            })

        return output_paragraphs

    def translate_chunk(self, chunk: str, request: TranslationRequest, conversation_history: List[dict]) -> tuple:
        conversation_history.append({"role": "user", "content": chunk})
        if len(conversation_history) > (request.max_context * 2 + 1):
            messages_to_send = [conversation_history[0]] + conversation_history[-(request.max_context * 2):]
        else:
            messages_to_send = conversation_history

        completion = self.provider.chat.completions.create(
            model='gpt-4o',
            messages=messages_to_send,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": reply})
        return reply, conversation_history 