from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

RUNBOOKS_DIR = Path("data/runbooks")


def load_runbooks() -> list[Document]:
    """Load Markdown runbooks as LangChain documents."""
    documents = []

    for file_path in RUNBOOKS_DIR.glob("*.md"):
        content = file_path.read_text(encoding="utf-8").strip()

        if content:
            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": file_path.name,
                        "path": str(file_path),
                    },
                )
            )

    return documents


def split_runbooks(
    documents: list[Document],
) -> list[Document]:
    """Split runbooks into smaller overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        add_start_index=True,
    )

    return splitter.split_documents(documents)


if __name__ == "__main__":
    runbooks = load_runbooks()
    chunks = split_runbooks(runbooks)

    print(f"Runbooks loaded: {len(runbooks)}")
    print(f"Chunks created: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n--- Chunk {index} ---")
        print(f"Source: {chunk.metadata['source']}")
        print(chunk.page_content)