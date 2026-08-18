import json
from pathlib import Path
from threading import Lock

# ============================================================
# CHAT HISTORY STORAGE
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CHAT_HISTORY_FILE = BASE_DIR / "chat_history.json"

_lock = Lock()


# ============================================================
# LOAD ALL CHAT HISTORY
# ============================================================

def _load_history():
    """
    Load all chat history from chat_history.json.
    """

    with _lock:

        if not CHAT_HISTORY_FILE.exists():
            return {}

        try:

            with open(
                CHAT_HISTORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(data, dict):
                    return data

                return {}

        except (
            json.JSONDecodeError,
            OSError
        ):

            return {}


# ============================================================
# SAVE ALL CHAT HISTORY
# ============================================================

def _save_history(history):
    """
    Save all chat history to chat_history.json.
    """

    with _lock:

        try:

            # Temporary file prevents partially written JSON
            temp_file = CHAT_HISTORY_FILE.with_suffix(
                ".tmp"
            )

            with open(
                temp_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    history,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            temp_file.replace(
                CHAT_HISTORY_FILE
            )

        except OSError as error:

            print(
                "Failed to save chat history:",
                error
            )


# ============================================================
# GET MEMORY
# ============================================================

def get_memory(
    session_id: str,
    collection: str = "default"
):
    """
    Return conversation history for a specific
    session + document.

    Example:

    session123 + resume
        -> resume conversation

    session123 + project
        -> project conversation
    """

    memory_key = (
        f"{session_id}::{collection}"
    )

    history = _load_history()

    if memory_key not in history:

        history[memory_key] = []

        _save_history(history)

    return history[memory_key]


# ============================================================
# ADD MESSAGE TO MEMORY
# ============================================================

def save_message(
    session_id: str,
    collection: str,
    question: str,
    answer: str
):
    """
    Save one question and answer permanently.
    """

    memory_key = (
        f"{session_id}::{collection}"
    )

    history = _load_history()

    if memory_key not in history:
        history[memory_key] = []

    history[memory_key].append(
        {
            "question": question,
            "answer": answer
        }
    )

    _save_history(history)

    print(
        f"Chat history saved successfully."
    )


# ============================================================
# CLEAR ONE DOCUMENT CHAT
# ============================================================

def clear_memory(
    session_id: str,
    collection: str = "default"
):
    """
    Clear conversation history for one
    session + document.
    """

    memory_key = (
        f"{session_id}::{collection}"
    )

    history = _load_history()

    if memory_key in history:

        del history[memory_key]

        _save_history(history)

        print(
            f"Chat history cleared: {memory_key}"
        )


# ============================================================
# CLEAR ENTIRE SESSION
# ============================================================

def clear_session(
    session_id: str
):
    """
    Clear all document conversations
    belonging to one session.
    """

    history = _load_history()

    prefix = (
        f"{session_id}::"
    )

    keys_to_delete = [
        key
        for key in history
        if key.startswith(prefix)
    ]

    for key in keys_to_delete:
        del history[key]

    if keys_to_delete:

        _save_history(history)

        print(
            f"Cleared {len(keys_to_delete)} "
            f"chat histories for session "
            f"{session_id}"
        )