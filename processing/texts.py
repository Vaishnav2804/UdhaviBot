def clean_text(text: str) -> str:
    """
    Clean the text by removing unwanted characters and formatting.
    """
    cleaned_text = text.replace("\n", " ").strip()
    return cleaned_text
