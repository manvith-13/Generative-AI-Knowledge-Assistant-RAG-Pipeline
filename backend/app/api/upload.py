from fastapi import APIRouter, UploadFile, File
import os
import shutil

from app.utils import sanitize_collection_name
from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.embeddings import get_embedding_model
from app.rag.vectorstore import create_vectorstore


router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # ============================================================
    # CHECK FILE TYPE
    # ============================================================

    if not file.filename.lower().endswith(".pdf"):
        return {
            "error": "Only PDF files are allowed."
        }

    # ============================================================
    # CREATE UPLOADS FOLDER
    # ============================================================

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    # ============================================================
    # SAVE UPLOADED FILE
    # ============================================================

    file_path = os.path.join(
        "uploads",
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    # ============================================================
    # CREATE VALID CHROMADB COLLECTION NAME
    # ============================================================

    collection_name = sanitize_collection_name(
        file.filename
    )

    print("\n" + "=" * 60)
    print("UPLOAD SUCCESS")
    print("=" * 60)

    print("Original filename:", file.filename)
    print("Collection:", collection_name)

    print("=" * 60)

    # ============================================================
    # PROCESS PDF
    # ============================================================

    try:

        # --------------------------------------------------------
        # LOAD PDF
        # --------------------------------------------------------

        documents = load_pdf(
            file_path
        )

        # --------------------------------------------------------
        # SPLIT DOCUMENTS
        # --------------------------------------------------------

        chunks = split_documents(
            documents
        )

        # --------------------------------------------------------
        # LOAD EMBEDDING MODEL
        # --------------------------------------------------------

        embeddings = get_embedding_model()

        # --------------------------------------------------------
        # STORE VECTORS IN CHROMADB
        # --------------------------------------------------------

        create_vectorstore(
            chunks,
            embeddings,
            collection_name
        )

        # --------------------------------------------------------
        # RETURN SUCCESS
        # --------------------------------------------------------

        return {
            "message": "PDF uploaded and indexed successfully!",
            "filename": file.filename,
            "collection": collection_name,
            "pages": len(documents),
            "chunks": len(chunks)
        }

    except Exception as e:

        print("\n" + "=" * 60)
        print("UPLOAD ERROR")
        print("=" * 60)

        print(str(e))

        print("=" * 60)

        return {
            "error": str(e)
        }