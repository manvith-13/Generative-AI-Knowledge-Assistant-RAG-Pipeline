from pathlib import Path

from langchain_chroma import Chroma

from app.utils import sanitize_collection_name


# ============================================================
# CHROMA DATABASE LOCATION
# ============================================================

CHROMA_DB_DIR = (
    Path(__file__).resolve().parents[2]
    / "chroma_db"
)


# ============================================================
# CREATE VECTOR STORE
# ============================================================

def create_vectorstore(
    chunks,
    embeddings,
    collection_name
):
    """
    Create and persist a Chroma vector store.
    """

    # --------------------------------------------------------
    # Make sure collection name is valid
    # --------------------------------------------------------

    collection_name = sanitize_collection_name(
        collection_name
    )

    print("\n" + "=" * 60)
    print("CREATING VECTOR STORE")
    print("=" * 60)

    print("Collection:", collection_name)

    # --------------------------------------------------------
    # Create Chroma vector store
    # --------------------------------------------------------

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(
            CHROMA_DB_DIR
        ),
        collection_name=collection_name,
    )

    # --------------------------------------------------------
    # Debug information
    # --------------------------------------------------------

    document_count = (
        vectorstore._collection.count()
    )

    print("=" * 60)
    print("UPLOAD SUCCESS")
    print("Collection:", collection_name)
    print(
        "Documents Stored:",
        document_count
    )
    print("=" * 60)

    return vectorstore