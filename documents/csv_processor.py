import pandas as pd


def extract_csv(file_path):
    """
    CSV file se tabular data extract karta hai.

    Har row ko text mein convert karta hai
    aur row number + source preserve karta hai.
    """

    dataframe = pd.read_csv(
        file_path
    )

    # Empty rows remove
    dataframe = dataframe.dropna(
        how="all"
    )

    documents = []

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
                "row": int(row_number) + 2
            }
        )

    return documents