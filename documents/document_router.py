from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".txt": "txt",
    ".xlsx": "xlsx",
    ".xls": "xls",
    ".csv": "csv",
}


def get_file_type(file_name):
    """
    File extension dekh kar document type return karta hai.
    """

    extension = Path(file_name).suffix.lower()

    return SUPPORTED_EXTENSIONS.get(extension)


def is_supported_file(file_name):
    """
    Check karta hai ke file hamari supported list mein hai ya nahi.
    """

    return get_file_type(file_name) is not None


def route_document(file_name):
    """
    File ko uske correct processor type ki taraf route karta hai.
    """

    file_type = get_file_type(file_name)

    if file_type is None:

        raise ValueError(
            f"Unsupported file type: {file_name}"
        )

    return file_type