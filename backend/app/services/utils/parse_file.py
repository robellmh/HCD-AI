from io import BytesIO
from typing import List

import PyPDF2


async def parse_file(file: bytes) -> List[str]:
    """Parse the content of an uploaded file into chunks.

    For PDFs, each page is treated as its own chunk.
    For text files, the content is split into chunks of fixed size.

    Parameters
    ----------
    file : bytes
        The content of the uploaded file.

    Returns
    -------
    List[str]
        A list of text chunks extracted from the file.
    """
    if file[:5] == b"%PDF-":
        pdf_reader = PyPDF2.PdfReader(BytesIO(file))
        chunks = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text and page_text.strip():
                chunks.append(page_text.strip())
        if not chunks:
            raise RuntimeError("No text could be extracted from the uploaded PDF file.")

    else:
        # Assume it's text
        text = file.decode("utf-8")
        if not text.strip():
            raise RuntimeError(
                "No text could be extracted from the uploaded text file."
            )
        chunk_size = 1000
        chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    return chunks
