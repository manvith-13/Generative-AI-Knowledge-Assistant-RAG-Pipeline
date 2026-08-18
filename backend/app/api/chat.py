from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pathlib import Path
import sqlite3
import json
from datetime import datetime

from app.utils import sanitize_collection_name
from app.rag.retriever import get_retriever
from app.rag.llm import get_llm


router = APIRouter()


# ============================================================
# DATABASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = BASE_DIR / "chat_history.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT NOT NULL,

            collection TEXT NOT NULL,

            question TEXT NOT NULL,

            answer TEXT NOT NULL,

            sources TEXT,

            created_at TEXT NOT NULL

        )
        """
    )

    connection.commit()

    connection.close()


# Initialize database
initialize_database()


# ============================================================
# REQUEST MODEL
# ============================================================

class QuestionRequest(BaseModel):

    question: str

    collection: str

    session_id: str


# ============================================================
# SAVE CHAT MESSAGE
# ============================================================

def save_chat_message(
    session_id: str,
    collection: str,
    question: str,
    answer: str,
    sources: list
):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO chat_history
        (
            session_id,
            collection,
            question,
            answer,
            sources,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            collection,
            question,
            answer,
            json.dumps(sources),
            datetime.now().isoformat()
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# GET CHAT HISTORY FROM SQLITE
# ============================================================

def get_chat_history(
    session_id: str,
    collection: str
):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            question,
            answer,
            sources,
            created_at

        FROM chat_history

        WHERE
            session_id = ?
            AND collection = ?

        ORDER BY id ASC
        """,
        (
            session_id,
            collection
        )
    )

    rows = cursor.fetchall()

    connection.close()

    history = []

    for row in rows:

        try:

            sources = json.loads(
                row["sources"]
            )

        except Exception:

            sources = []

        # ----------------------------------------------------
        # USER MESSAGE
        # ----------------------------------------------------

        history.append(
            {
                "role": "user",

                "content": row["question"],

                "created_at":
                    row["created_at"]
            }
        )

        # ----------------------------------------------------
        # ASSISTANT MESSAGE
        # ----------------------------------------------------

        history.append(
            {
                "role": "assistant",

                "content": row["answer"],

                "sources": sources,

                "created_at":
                    row["created_at"]
            }
        )

    return history


# ============================================================
# GET CHAT HISTORY API
# ============================================================

@router.get(
    "/chat/{session_id}/{collection}"
)
async def get_chat(
    session_id: str,
    collection: str
):

    collection_name = sanitize_collection_name(
        collection
    )

    try:

        history = get_chat_history(
            session_id,
            collection_name
        )

    except Exception as error:

        print(
            "Chat history error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to load chat history."
        )

    print("\n" + "=" * 70)

    print("CHAT HISTORY REQUEST")

    print("=" * 70)

    print(
        "Session ID:",
        session_id
    )

    print(
        "Collection:",
        collection_name
    )

    print(
        "Messages:",
        len(history)
    )

    print("=" * 70)

    return {

        "session_id":
            session_id,

        "collection":
            collection_name,

        "messages":
            history
    }


# ============================================================
# ASK QUESTION
# ============================================================

@router.post("/ask")
async def ask_question(
    request: QuestionRequest
):

    print("\n" + "=" * 70)

    print("NEW QUESTION")

    print("=" * 70)

    print(
        "Question:",
        request.question
    )

    print(
        "Collection received:",
        request.collection
    )

    print(
        "Session ID:",
        request.session_id
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    question = request.question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    if not request.collection:

        raise HTTPException(
            status_code=400,
            detail="Collection is required."
        )

    if not request.session_id:

        raise HTTPException(
            status_code=400,
            detail="Session ID is required."
        )


    # ========================================================
    # SANITIZE COLLECTION
    # ========================================================

    collection_name = sanitize_collection_name(
        request.collection
    )

    print(
        "Collection used:",
        collection_name
    )


    # ========================================================
    # LOAD RETRIEVER
    # ========================================================

    try:

        retriever = get_retriever(
            collection_name
        )

    except Exception as error:

        print(
            "Retriever error:",
            error
        )

        raise HTTPException(
            status_code=404,
            detail=(
                "The selected document "
                "could not be found."
            )
        )


    # ========================================================
    # LOAD PREVIOUS CHAT HISTORY
    # ========================================================

    try:

        previous_messages = get_chat_history(
            request.session_id,
            collection_name
        )

    except Exception as error:

        print(
            "Chat history loading error:",
            error
        )

        previous_messages = []


    # ========================================================
    # BUILD CONVERSATION HISTORY
    # ========================================================

    history = ""

    # Last 10 messages
    recent_messages = previous_messages[-10:]

    for message in recent_messages:

        if message["role"] == "user":

            history += (
                f"User: "
                f"{message['content']}\n"
            )

        elif message["role"] == "assistant":

            history += (
                f"Assistant: "
                f"{message['content']}\n"
            )


    print("\nConversation History:")

    if history:

        print(history)

    else:

        print(
            "No previous conversation."
        )


    # ========================================================
    # BUILD RETRIEVAL QUERY
    # ========================================================

    retrieval_query = question

    if history:

        retrieval_query = f"""
Previous conversation:

{history}

Current question:

{question}

Use the previous conversation to
understand references in the current
question.

Retrieve information from the uploaded
document that is needed to answer the
current question.
"""


    print("\nRetrieval Query:")

    print(retrieval_query)


    # ========================================================
    # RETRIEVE DOCUMENT CHUNKS
    # ========================================================

    try:

        docs = retriever.invoke(
            retrieval_query
        )

    except Exception as error:

        print(
            "Retrieval error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve "
                "information from the document."
            )
        )


    # ========================================================
    # DEBUG RETRIEVED DOCUMENTS
    # ========================================================

    print("\n" + "=" * 70)

    print("RETRIEVED CHUNKS")

    print("=" * 70)


    for index, doc in enumerate(docs):

        print(
            f"\nChunk {index + 1}"
        )

        print("Content:")

        print(
            doc.page_content
        )

        print("\nMetadata:")

        print(
            doc.metadata
        )

        print(
            "-" * 70
        )


    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    if not context.strip():

        answer = (
            "I couldn't find that information "
            "in the uploaded document."
        )

    else:

        # ====================================================
        # LOAD LLM
        # ====================================================

        try:

            llm = get_llm()

        except Exception as error:

            print(
                "LLM initialization error:",
                error
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to initialize "
                    "the AI model."
                )
            )


        # ====================================================
        # PROMPT
        # ====================================================

        prompt = f"""
You are an intelligent document assistant.

Your job is to answer the user's question
using the information contained in the
uploaded document.

IMPORTANT RULES:

1. Use the retrieved document context as
   your primary source of truth.

2. Use the previous conversation to
   understand references and follow-up
   questions.

3. You ARE allowed to make reasonable
   comparisons, evaluations, rankings,
   and conclusions based on facts
   explicitly present in the document.

4. For questions such as:

   - Which project is best?
   - Which project is strongest?
   - Which skill is most important?
   - Which experience is most relevant?
   - Why is this project better?

   compare the relevant information from
   the document and explain your reasoning.

5. Do NOT require the document to explicitly
   say that something is "best" or "better".

6. Every important claim in your answer must
   be supported by information from the
   retrieved document context.

7. Do NOT invent technologies, achievements,
   scores, responsibilities, or experiences
   that are not present in the document.

8. If the document genuinely does not contain
   enough information to answer the question,
   reply exactly:

"I couldn't find that information in the
uploaded document."

9. Give a direct and useful answer.

10. Do not mention retrieval, chunks,
    embeddings, vector databases, prompts,
    or internal system details unless the
    user specifically asks about them.

Previous Conversation:

{history}

Retrieved Document Context:

{context}

Current User Question:

{question}

Answer:
"""


        # ====================================================
        # CALL GEMINI
        # ====================================================

        try:

            response = llm.invoke(
                prompt
            )

        except Exception as error:

            print(
                "LLM error:",
                error
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "The AI model failed "
                    "to generate a response."
                )
            )


        # ====================================================
        # EXTRACT ANSWER
        # ====================================================

        answer = response.content


        if isinstance(
            answer,
            list
        ):

            answer = "\n".join(
                item.get(
                    "text",
                    ""
                )
                for item in answer
                if isinstance(
                    item,
                    dict
                )
            )

        elif not isinstance(
            answer,
            str
        ):

            answer = str(
                answer
            )


        answer = answer.strip()


    # ========================================================
    # BUILD SOURCES
    # ========================================================

    sources = []

    seen_sources = set()


    for doc in docs:

        page = doc.metadata.get(
            "page",
            "Unknown"
        )

        chunk_id = doc.metadata.get(
            "chunk_id",
            "Unknown"
        )

        source = doc.metadata.get(
            "source",
            "Unknown"
        )


        source_key = (
            str(page),
            str(chunk_id),
            str(source)
        )


        if source_key in seen_sources:

            continue


        seen_sources.add(
            source_key
        )


        sources.append(
            {
                "page": page,

                "chunk_id":
                    chunk_id,

                "source":
                    source
            }
        )


    # ========================================================
    # SAVE CHAT TO SQLITE
    # ========================================================

    try:

        save_chat_message(
            session_id=
                request.session_id,

            collection=
                collection_name,

            question=
                question,

            answer=
                answer,

            sources=
                sources
        )

        print(
            "\nCHAT HISTORY SAVED SUCCESSFULLY"
        )

    except Exception as error:

        print(
            "\nChat history save error:",
            error
        )


    print("\n" + "=" * 70)

    print(
        "FINAL ANSWER:"
    )

    print(answer)

    print(
        "\nSources:",
        len(sources)
    )

    print("=" * 70)


    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return {

        "question":
            question,

        "collection":
            collection_name,

        "session_id":
            request.session_id,

        "answer":
            answer,

        "sources":
            sources
    }


# ============================================================
# CLEAR CHAT
# ============================================================

@router.delete(
    "/chat/{session_id}/{collection}"
)
async def clear_chat(
    session_id: str,
    collection: str
):

    collection_name = sanitize_collection_name(
        collection
    )


    connection = get_db_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        DELETE FROM chat_history

        WHERE
            session_id = ?
            AND collection = ?
        """,
        (
            session_id,
            collection_name
        )
    )


    deleted_count = cursor.rowcount


    connection.commit()

    connection.close()


    print("\n" + "=" * 70)

    print("CHAT CLEARED")

    print("=" * 70)

    print(
        "Session ID:",
        session_id
    )

    print(
        "Collection:",
        collection_name
    )

    print(
        "Deleted messages:",
        deleted_count
    )

    print("=" * 70)


    return {

        "message":
            "Conversation cleared successfully",

        "session_id":
            session_id,

        "collection":
            collection_name,

        "deleted_messages":
            deleted_count
    }