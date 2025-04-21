import pytest
from unittest.mock import patch, MagicMock
from latin_translator.service.letter_translator import LetterTranslator
from latin_translator.models import TranslationStages
from latin_translator.utils import split_paragraphs, split_text_with_quotes


class TestLetterTranslator:
    """Tests for the LetterTranslator class"""

    @pytest.fixture
    def translator(self):
        """Fixture to create a translator with mocked methods"""
        # Mock _load_prompts to avoid file reading
        with patch.object(LetterTranslator, '_load_prompts'):
            translator = LetterTranslator()
            # Set prompts directly
            translator.direct_prompt = "Translate Latin to English literally"
            translator.rewrite_prompt = "Rewrite the English translation"
            return translator

    def test_lone_quotation_marks_handling(self, translator):
        """
        Test that lone quotation marks are handled correctly.
        
        This test verifies the fix for an issue where an LLM would generate unwanted content
        for lone quotation marks (like ' or ") instead of preserving them as-is.
        """
        # Simple test case with a lone closing quotation mark
        simple_test = """Sic enim coepit: 'noli, mi Marcelline, torqueri tamquam de re magna deliberes.
Non est res magna vivere: omnes servi tui vivunt, omnia animalia: magnum est honeste mori, prudenter, fortiter.
Cogita quamdiu iam idem facias: cibus, somnus, libido -- per hunc circulum curritur; mori velle non tantum prudens aut fortis aut miser, etiam fastidiosus potest.
'"""

        # Real example from the notebook that originally showed the issue
        real_example = """[6] Amicus noster Stoicus, homo egregius et, ut verbis illum quibus laudari dignus est laudem, vir fortis ac strenuus, videtur mihi optime illum cohortatus. Sic enim coepit: 'noli, mi Marcelline, torqueri tamquam de re magna deliberes. Non est res magna vivere: omnes servi tui vivunt, omnia animalia: magnum est honeste mori, prudenter, fortiter. Cogita quamdiu iam idem facias: cibus, somnus, libido -- per hunc circulum curritur; mori velle non tantum prudens aut fortis aut miser, etiam fastidiosus potest.'"""

        # Mock the translate_chunk method to track API calls and verify behavior
        api_call_count = 0
        original_translate_chunk = translator.translate_chunk
        
        def mock_translate_chunk(text, system_prompt, conversation_history=None):
            nonlocal api_call_count
            
            # Use the real implementation but count API calls
            if len(text.strip()) <= 2 and all(char in "'\"" for char in text.strip()):
                # This should skip the API call for lone quotes
                result = original_translate_chunk(text, system_prompt, conversation_history)
                # Verify the translation is exactly the input text (preserved)
                assert result[0] == text
                return result
            
            # For non-quote text, count the API call
            api_call_count += 1
            
            # Return a simple mock response for regular text
            if conversation_history is None:
                conversation_history = []
            return text, conversation_history  # Just echo back the text for testing
        
        # Test the simple case
        with patch.object(translator, 'translate_chunk', side_effect=mock_translate_chunk):
            # First check that our simple text is split as expected
            paragraphs = split_paragraphs(simple_test)
            sentences = split_text_with_quotes(paragraphs[0])
            assert len(sentences) == 4
            assert sentences[3] == "'"  # Last sentence is just a quote
            
            # Process the paragraph
            result = translator.process_letter(simple_test)
            
            # Verify results - especially that the lone quote is preserved
            assert len(result) == 1  # One paragraph
            assert len(result[0].original) == 4
            assert result[0].original[3] == "'"
            assert result[0].direct[3] == "'"
            assert result[0].rhetorical[3] == "'"
            
            # Exact API call count for the simple case should be 6:
            # 3 sentences × 2 translation phases, but NOT the lone quotation mark
            assert api_call_count == 6
            
            # Reset API call counter for next test
            api_call_count = 0
            
            # Now test the real example
            paragraphs = split_paragraphs(real_example)
            sentences = split_text_with_quotes(paragraphs[0])
            assert len(sentences) == 5  # The real example also has a lone quote
            
            result = translator.process_letter(real_example)
            
            # Verify results
            assert len(result) == 1
            assert len(result[0].original) == 5
            assert result[0].original[4] == "'"
            assert result[0].direct[4] == "'"
            assert result[0].rhetorical[4] == "'"
            
            # Should be 8 API calls for the real example:
            # 4 sentences × 2 translation phases, without calling API for lone quote
            assert api_call_count == 8

    def test_demonstration_of_previous_bug(self, translator):
        """
        This test demonstrates the previous bug behavior for documentation purposes.
        
        It shows how, before the fix, the model would generate unwanted conversational
        text for a lone quotation mark instead of preserving it as-is.
        """
        # This test is kept for documentation purposes only, to show the issue that was fixed
        test_paragraph = """Sic enim coepit: 'noli, mi Marcelline, torqueri tamquam de re magna deliberes.
Non est res magna vivere: omnes servi tui vivunt, omnia animalia: magnum est honeste mori, prudenter, fortiter.
Cogita quamdiu iam idem facias: cibus, somnus, libido -- per hunc circulum curritur; mori velle non tantum prudens aut fortis aut miser, etiam fastidiosus potest.
'"""

        # Mock the translate_chunk to show the previous buggy behavior
        def problematic_translate_chunk(text, system_prompt, conversation_history=None):
            # Simulate pre-fix behavior where direct translations work but rhetorical ones fail
            if system_prompt == translator.direct_prompt:
                if text == "'":  # Direct translation preserves quote
                    return "'", conversation_history or []
            elif system_prompt == translator.rewrite_prompt:
                if text == "'":  # Rhetorical translation adds unwanted text
                    return "If you have more text for me to work on or any questions, feel free to share!", conversation_history or []
            
            # For all other text, just echo it back
            return text, conversation_history or []
        
        with patch.object(translator, 'translate_chunk', side_effect=problematic_translate_chunk):
            result = translator.process_letter(test_paragraph)
            
            # Verify the bug would have manifested
            assert result[0].original[3] == "'"
            assert result[0].direct[3] == "'"
            # This unwanted text was the bug
            assert result[0].rhetorical[3] == "If you have more text for me to work on or any questions, feel free to share!" 