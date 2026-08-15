def extract_txt(file_path):
    """
    TXT file se text extract karta hai.
    """

    documents = []

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        text = file.read()

    if text.strip():

        documents.append(
            {
                "text": text.strip(),
                "source": file_path
            }
        )

    return documents