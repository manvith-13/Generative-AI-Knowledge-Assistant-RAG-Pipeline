from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):
    """
    Split documents into smaller chunks while preserving metadata.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    chunks = text_splitter.split_documents(
        documents
    )

    # --------------------------------------------------------
    # Add metadata to every chunk
    # --------------------------------------------------------

    for i, chunk in enumerate(chunks):

        chunk.metadata["chunk_id"] = i

        # Ensure page number exists
        if "page" not in chunk.metadata:

            chunk.metadata["page"] = 0

    return chunks