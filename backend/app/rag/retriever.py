from pathlib import Path

from langchain_chroma import Chroma

from app.utils import sanitize_collection_name
from app.rag.embeddings import get_embedding_model


# ============================================================
# CHROMA DATABASE LOCATION
# ============================================================

CHROMA_DB_DIR = (
    Path(__file__).resolve().parents[2]
    / "chroma_db"
)


# ============================================================
# GET RETRIEVER
# ============================================================

def get_retriever(collection_name: str):

    # --------------------------------------------------------
    # Make sure collection name is valid
    # --------------------------------------------------------

    collection_name = sanitize_collection_name(
        collection_name
    )

    print("\n" + "=" * 60)
    print("LOADING RETRIEVER")
    print("=" * 60)

    print("Collection:", collection_name)
    print("Chroma DB:", CHROMA_DB_DIR)

    # --------------------------------------------------------
    # Load embedding model
    # --------------------------------------------------------

    embeddings = get_embedding_model()

    # --------------------------------------------------------
    # Connect to ChromaDB
    # --------------------------------------------------------

    vectorstore = Chroma(
        persist_directory=str(
            CHROMA_DB_DIR
        ),
        embedding_function=embeddings,
        collection_name=collection_name,
    )

    # --------------------------------------------------------
    # Show collection information
    # --------------------------------------------------------

    document_count = (
        vectorstore._collection.count()
    )

    print(
        "Documents in Collection:",
        document_count
    )

    print("=" * 60)

    # --------------------------------------------------------
    # Create retriever
    # --------------------------------------------------------

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 15,
            "lambda_mult": 0.7,
        },
    )

    return retriever