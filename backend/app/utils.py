import re


def sanitize_collection_name(
    filename: str
) -> str:
    """
    Convert a PDF filename into a valid
    ChromaDB collection name.

    Example:
    MANVITH AI resume.pdf
    ->
    MANVITH_AI_resume
    """

    # Remove .pdf extension
    name = re.sub(
        r"\.pdf$",
        "",
        filename,
        flags=re.IGNORECASE
    )

    # Replace invalid characters
    name = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        name
    )

    # Remove repeated underscores
    name = re.sub(
        r"_+",
        "_",
        name
    )

    # Remove invalid beginning/end
    name = name.strip("_-")

    # ChromaDB minimum length
    if len(name) < 3:
        name = f"doc_{name}"

    # ChromaDB maximum length
    name = name[:512]

    # Make sure it doesn't end incorrectly
    name = name.rstrip("_-")

    return name