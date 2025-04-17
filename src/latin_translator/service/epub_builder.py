from datetime import datetime
import logging
from pathlib import Path
from typing import Optional, List

from ebooklib import epub
from pydantic import BaseModel

from ..models import Letter


class EpubConfig(BaseModel):
    """Configuration for EPUB generation."""
    title_template: str = "Seneca's Letters – {timestamp}"
    author: str = "Seneca"
    language: str = "en"
    style: str = '''
        @namespace epub "http://www.idpf.org/2007/ops";
        body { font-family: Times, serif; margin: 20px; }
        h1 { text-align: center; }
        p { text-align: justify; }
    '''


class EpubBuilder:
    """Builder for creating EPUBs from Letters."""
    
    def __init__(self, config: Optional[EpubConfig] = None):
        """Initialize a new EPUB builder with optional configuration."""
        self.config = config or EpubConfig()
        self.book = epub.EpubBook()
        self.chapters: List[epub.EpubHtml] = []
        self.logger = logging.getLogger(__name__)
        
        # Set initial metadata
        timestamp = datetime.now().strftime("%B %d, %Y")
        self.book.set_title(self.config.title_template.format(timestamp=timestamp))
        self.book.set_language(self.config.language)
        self.book.add_author(self.config.author)
        
        # Add stylesheet
        self.book.add_item(epub.EpubItem(
            uid="style",
            file_name="style/main.css",
            media_type="text/css",
            content=self.config.style
        ))
    
    def add_letter(self, letter: Letter, translation: str) -> 'EpubBuilder':
        """
        Add a letter to the EPUB.
        
        Args:
            letter: The Letter to add
            translation: The translated text of the letter
            
        Returns:
            self for method chaining
        """
        # Create chapter
        chapter = epub.EpubHtml(
            title=f"Letter {letter.number}: {letter.title}",
            file_name=f"letter_{letter.number}.xhtml"
        )
        
        # Log the head of the translated letter
        preview_length = 100  # Characters to preview
        translation_preview = translation[:preview_length] + ('...' if len(translation) > preview_length else '')
        self.logger.info(f"Adding Letter {letter.number}: {letter.title} - Preview: {translation_preview}")
        
        # Add content
        chapter.content = f'''
            <h1>Letter {letter.number}: {letter.title}</h1>
            <p>{translation.replace(chr(10), "<br/>")}</p>
        '''
        
        self.book.add_item(chapter)
        self.chapters.append(chapter)
        return self
    
    def save(self, output_path: Optional[Path] = None) -> Path:
        """
        Save the EPUB to a file.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path to the generated EPUB file
        """
        if not self.chapters:
            raise ValueError("Cannot create EPUB: no letters added")
            
        # Add navigation
        self.book.toc = [(epub.Section('Letters'), self.chapters)]
        self.book.spine = ['nav'] + self.chapters
        
        # Add required elements
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"seneca_letters_{timestamp}.epub")
        
        # Write EPUB file
        self.logger.info(f"Saving EPUB to {output_path}")
        epub.write_epub(str(output_path), self.book)
        return output_path 