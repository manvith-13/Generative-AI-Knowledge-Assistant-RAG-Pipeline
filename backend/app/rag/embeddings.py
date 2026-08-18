from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
#hii

@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load and cache the embedding model.
    """

    print("\n" + "=" * 60)
    print("LOADING EMBEDDING MODEL")
    print("=" * 60)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print(
        "Embedding Model:",
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    print("=" * 60)

    return embeddings