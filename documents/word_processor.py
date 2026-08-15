from docx import Document


def extract_docx(file_path):
    """
    DOCX file se text extract karta hai.

    Har paragraph ko separately process karta hai
    aur source + paragraph number preserve karta hai.
    """

    document = Document(file_path)

    documents = []

    for paragraph_number, paragraph in enumerate(
        document.paragraphs,
        start=1
    ):

        text = paragraph.text.strip()

        if not text:
            continue

        documents.append(
            {
                "text": text,
                "source": file_path,
                "paragraph": paragraph_number
            }
        )

    return documents