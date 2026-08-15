from pypdf import PdfReader


def extract_pdf(file_path):
    """
    PDF se text extract karta hai.

    Har page ka text aur page number preserve
    kiya jata hai taake baad mein source/page
    show kiya ja sake.
    """

    reader = PdfReader(file_path)

    documents = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text()

        if not text:
            continue

        documents.append(
            {
                "text": text.strip(),
                "source": file_path,
                "page": page_number
            }
        )

    return documents