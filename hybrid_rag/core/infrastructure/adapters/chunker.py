from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.application.interfaces import Chunker


class LangchainChunker(Chunker):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 120):
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def split(self, text: str, source: str) -> list[dict]:
        docs = self.splitter.create_documents([text], metadatas=[{"source": source}])
        return [{"text": doc.page_content, "metadata": doc.metadata} for doc in docs]
