from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys
import chromadb

from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.utils import sanitize_collection_name


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

UPLOAD_DIR = BASE_DIR / "uploads"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"


print("=" * 60)
print("FASTAPI STARTING")
print("Python:", sys.executable)
print("Base Directory:", BASE_DIR)
print("Upload Directory:", UPLOAD_DIR)
print("ChromaDB Directory:", CHROMA_DB_DIR)
print("=" * 60)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Generative AI Knowledge Assistant",
    description="Production-ready RAG application using FastAPI",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(upload_router)
app.include_router(chat_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to the Generative AI Knowledge Assistant 🚀"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "Backend is running successfully!"
    }


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

@app.get("/documents")
def get_documents():

    print("\n" + "=" * 60)
    print("GET DOCUMENTS")
    print("=" * 60)

    # Make sure uploads directory exists
    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    documents = []

    for file in UPLOAD_DIR.iterdir():

        if (
            file.is_file()
            and file.suffix.lower() == ".pdf"
        ):
            documents.append(file.name)

    # Sort alphabetically
    documents.sort(
        key=lambda name: name.lower()
    )

    print("Documents found:", len(documents))

    for document in documents:
        print(" -", document)

    print("=" * 60)

    return {
        "documents": documents,
        "count": len(documents)
    }


# ============================================================
# DELETE DOCUMENT
# ============================================================

@app.delete("/documents/{filename}")
def delete_document(filename: str):

    print("\n" + "=" * 60)
    print("DELETE DOCUMENT")
    print("=" * 60)

    print("Requested filename:", filename)

    # --------------------------------------------------------
    # SECURITY CHECK
    # --------------------------------------------------------

    safe_filename = Path(filename).name

    if safe_filename != filename:

        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    # --------------------------------------------------------
    # ONLY PDF FILES
    # --------------------------------------------------------

    if not filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF documents can be deleted."
        )

    # --------------------------------------------------------
    # FILE PATH
    # --------------------------------------------------------

    file_path = UPLOAD_DIR / filename

    print("File path:", file_path)

    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {filename}"
        )

    # --------------------------------------------------------
    # USE THE SAME COLLECTION SANITIZER AS UPLOAD
    # --------------------------------------------------------

    collection_name = sanitize_collection_name(
        filename
    )

    print("Collection name:", collection_name)

    # --------------------------------------------------------
    # DELETE CHROMADB COLLECTION
    # --------------------------------------------------------

    chroma_deleted = False

    try:

        if CHROMA_DB_DIR.exists():

            client = chromadb.PersistentClient(
                path=str(CHROMA_DB_DIR)
            )

            try:

                client.delete_collection(
                    name=collection_name
                )

                chroma_deleted = True

                print(
                    "ChromaDB collection deleted:",
                    collection_name
                )

            except Exception as chroma_error:

                print(
                    "ChromaDB collection was not found "
                    "or was already deleted."
                )

                print(
                    "ChromaDB message:",
                    chroma_error
                )

        else:

            print(
                "ChromaDB directory does not exist."
            )

    except Exception as error:

        print(
            "ChromaDB deletion error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to delete ChromaDB collection: "
                f"{str(error)}"
            )
        )

    # --------------------------------------------------------
    # DELETE PDF FILE
    # --------------------------------------------------------

    try:

        file_path.unlink()

        print(
            "PDF deleted successfully:",
            filename
        )

    except Exception as error:

        print(
            "PDF deletion error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to delete PDF file: "
                f"{str(error)}"
            )
        )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    print("=" * 60)

    return {
        "message": "Document deleted successfully.",
        "filename": filename,
        "collection": collection_name,
        "chroma_deleted": chroma_deleted
    }