from datetime import datetime
from ebooklib import epub
from ..models import Letter

def create_epub(letter: Letter, translation: str) -> epub.EpubBook:
    """Create an EPUB book from a translated letter."""
    # Create a new EPUB book
    book = epub.EpubBook()

    # Format current time as "May 5th 12:11p"
    now = datetime.now()
    day = now.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    formatted_time = now.strftime(f"%B {day}{suffix} %I:%M%p").lower().replace("am", "a").replace("pm", "p")

    # Set title with readable datetime
    book.set_title(f"Seneca's Letters – {formatted_time}")

    # Set metadata
    book.set_identifier('seneca_letters')
    book.set_language('en')
    book.add_author('Seneca')

    # Create a chapter
    translation_html = translation.replace("\n", "<br/>")
    chapter = epub.EpubHtml(
        title=f"Letter {letter.number} {letter.title}",
        file_name=f"letter_{letter.number}.xhtml",
        lang='en'
    )
    chapter.content = f'<h1>Letter {letter.number}</h1><p>{translation_html}</p>'

    # Add the chapter
    book.add_item(chapter)

    # Define Table of Contents
    book.toc = (epub.Link(
        f'letter_{letter.number}.xhtml',
        f'Letter {letter.number}',
        f'chap_{letter.number}'
    ),)

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: Times, serif;
        margin-left: 20px;
        margin-right: 20px;
    }
    h1 {
        text-align: center;
    }
    p {
        text-align: justify;
    }
    '''

    # Add CSS file
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style
    )
    book.add_item(nav_css)

    # Set the spine
    book.spine = ['nav', chapter]

    return book 