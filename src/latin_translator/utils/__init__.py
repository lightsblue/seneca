"""Utility modules for the Latin Translator project.

This package contains various utility modules used across the project:
- text_utils: Text processing and manipulation utilities
- logging_config: Logging configuration and management
"""

from .text_utils import (
    split_paragraphs,
    split_text_with_quotes,
    split_naive_sentences,
    extract_outer_quoted_parts,
    clean_translation,
)

from .logging_config import LoggingManager

__all__ = [
    # Text utilities
    'split_paragraphs',
    'split_text_with_quotes',
    'split_naive_sentences',
    'extract_outer_quoted_parts',
    'clean_translation',
    
    # Logging utilities
    'LoggingManager',
] 