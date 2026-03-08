"""Document parsing and chunking services"""

import time
import tiktoken
from typing import Optional, List, Dict, Generator
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document as DocxDocument
import markdown


class DocumentParser:
    """Document parser supporting multiple file formats"""

    SUPPORTED_FORMATS = {".pdf", ".docx", ".md", ".txt"}

    @staticmethod
    def is_supported(file_path: str) -> bool:
        """Check if file format is supported"""
        return Path(file_path).suffix.lower() in DocumentParser.SUPPORTED_FORMATS

    @staticmethod
    def parse(file_path: str) -> tuple[str, Dict]:
        """
        Parse document and return text content with metadata

        Returns:
            text: Extracted text content
            metadata: Dictionary with parsing metadata
        """
        start_time = time.time()
        file_path = Path(file_path)
        file_type = file_path.suffix.lower()
        file_size = file_path.stat().st_size

        if file_type == ".pdf":
            text, pages = DocumentParser._parse_pdf(file_path)
            metadata = {
                "file_type": "pdf",
                "file_size": file_size,
                "page_count": pages,
                "parse_time": time.time() - start_time,
            }
        elif file_type == ".docx":
            text = DocumentParser._parse_docx(file_path)
            metadata = {
                "file_type": "docx",
                "file_size": file_size,
                "parse_time": time.time() - start_time,
            }
        elif file_type == ".md":
            text = DocumentParser._parse_md(file_path)
            metadata = {
                "file_type": "markdown",
                "file_size": file_size,
                "parse_time": time.time() - start_time,
            }
        elif file_type == ".txt":
            text = DocumentParser._parse_txt(file_path)
            metadata = {
                "file_type": "txt",
                "file_size": file_size,
                "parse_time": time.time() - start_time,
            }
        else:
            raise ValueError(f"Unsupported file format: {file_type}")

        # Clean text
        text = DocumentParser._clean_text(text)

        return text, metadata

    @staticmethod
    def _parse_pdf(file_path: Path) -> tuple[str, int]:
        """Parse PDF using PyMuPDF"""
        doc = fitz.open(str(file_path))
        text_parts = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text_parts.append(f"\n\n[Page {page_num + 1}]\n")
            text_parts.append(page.get_text())

        doc.close()
        return "".join(text_parts), len(doc)

    @staticmethod
    def _parse_docx(file_path: Path) -> str:
        """Parse DOCX using python-docx"""
        doc = DocxDocument(str(file_path))
        text_parts = []

        for paragraph in doc.paragraphs:
            text_parts.append(paragraph.text)

        return "\n".join(text_parts)

    @staticmethod
    def _parse_md(file_path: Path) -> str:
        """Parse Markdown file"""
        return file_path.read_text(encoding="utf-8")

    @staticmethod
    def _parse_txt(file_path: Path) -> str:
        """Parse plain text file"""
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ["gbk", "gb2312", "latin1"]:
                try:
                    return file_path.read_text(encoding=encoding)
                except UnicodeDecodeError:
                    continue
        raise ValueError("Unable to decode text file")

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = "\n".join(line.strip() for line in text.split("\n") if line.strip())

        # Remove empty lines
        text = "\n".join(line for line in text.split("\n") if line.strip())

        return text.strip()


class DocumentChunker:
    """Document chunker with configurable size and overlap"""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: float = 0.1,
        tokenizer: Optional[str] = None,
    ):
        """
        Initialize document chunker

        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Overlap ratio (0.0 to 0.5)
            tokenizer: Tokenizer to use (cl100k_base for GPT models)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = int(chunk_size * min(chunk_overlap, 0.5))

        # Get tokenizer
        if tokenizer is None:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        else:
            self.tokenizer = tiktoken.get_encoding(tokenizer)

    def split_text(
        self,
        text: str,
        metadata: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Split text into overlapping chunks

        Args:
            text: Input text
            metadata: Base metadata to include in each chunk

        Returns:
            List of chunk dictionaries with content and metadata
        """
        if not text:
            return []

        metadata = metadata or {}

        # Get tokens
        tokens = self.tokenizer.encode(text)
        token_count = len(tokens)

        if token_count <= self.chunk_size:
            return [{
                "content": text,
                "metadata": {
                    **metadata,
                    "chunk_index": 0,
                    "chunk_count": 1,
                    "token_count": token_count,
                },
            }]

        # Split into chunks
        chunks = []
        chunk_index = 0
        start = 0

        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))

            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)

            chapters = metadata.get("chunk_index", chunk_index)
            chunks.append({
                "content": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk_index": chunk_index,
                    "chunk_count": (len(tokens) + self.chunk_size - 1) // self.chunk_size,
                    "token_count": len(chunk_tokens),
                    "char_start": start,
                    "char_end": end,
                },
            })

            chunk_index += 1
            start = end - self.chunk_overlap

        return chunks

    def split_text_with_page_numbers(
        self,
        text: str,
        metadata: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Split text while preserving page numbers

        This is useful for PDF documents where page information is important
        """
        metadata = metadata or {}

        # Split by page markers if present
        if "[Page" in text:
            pages = []
            current_page = 1

            # Find all page markers
            import re
            page_pattern = r"\[Page (\d+)\]"

            parts = []
            last_end = 0

            for match in re.finditer(page_pattern, text):
                if match.start() > last_end:
                    parts.append((current_page, text[last_end:match.start()]))
                current_page = int(match.group(1))
                last_end = match.end()

            if last_end < len(text):
                parts.append((current_page, text[last_end:]))

            # Process each page
            all_chunks = []
            for page_num, page_text in parts:
                page_metadata = {**metadata, "page_num": page_num}
                chunks = self.split_text(page_text, page_metadata)

                # Adjust chunk_index to be global
                for chunk in chunks:
                    chunk["metadata"]["chunk_index"] = len(all_chunks)

                all_chunks.extend(chunks)

            return all_chunks
        else:
            # No page markers, just split normally
            return self.split_text(text, metadata)

    def get_chunk_count(self, text: str) -> int:
        """Get the number of chunks the text will be split into"""
        if not text:
            return 0

        tokens = self.tokenizer.encode(text)
        token_count = len(tokens)

        if token_count <= self.chunk_size:
            return 1

        return (token_count + self.chunk_size - 1) // self.chunk_size


# Chunk metadata schema for API
class ChunkMetadata:
    """Schema for chunk metadata"""

    kb_id: str
    doc_id: str
    doc_name: str
    chunk_index: int
    chunk_count: int
    token_count: int
    page_num: Optional[int] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None
