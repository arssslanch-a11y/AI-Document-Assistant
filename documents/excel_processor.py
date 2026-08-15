from pathlib import Path
import pandas as pd


def extract_excel(file_path):
    """
    XLSX aur XLS files se data extract karta hai.

    Har sheet ko separately process karta hai.
    Sheet name, row number aur source preserve karta hai.
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".xlsx":
        excel_file = pd.ExcelFile(
            file_path,
            engine="openpyxl"
        )

    elif extension == ".xls":
        excel_file = pd.ExcelFile(
            file_path,
            engine="xlrd"
        )

    else:
        raise ValueError(
            f"Unsupported Excel file: {file_path}"
        )

    documents = []

    for sheet_name in excel_file.sheet_names:

        dataframe = pd.read_excel(
            excel_file,
            sheet_name=sheet_name
        )

        # Empty rows/columns remove
        dataframe = dataframe.dropna(
            how="all"
        )

        if dataframe.empty:
            continue

        for row_number, row in dataframe.iterrows():

            values = []

            for column_name, value in row.items():

                if pd.notna(value):

                    values.append(
                        f"{column_name}: {value}"
                    )

            if not values:
                continue

            text = "\n".join(values)

            documents.append(
                {
                    "text": text,
                    "source": str(file_path),
                    "sheet": sheet_name,
                    "row": int(row_number) + 2
                }
            )

    return documents