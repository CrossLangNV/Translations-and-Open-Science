import os

import pandas as pd
from translate.storage.tmx import tmxfile


def read_lines(filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Cleanup (remove newlines)
    lines = [line.strip() for line in lines]

    return lines


def create_TMX(
    df: pd.DataFrame,
    filename_tmx: str,
    INPUT_FOLDER: str,
    pub_geo: dict = {},
    verbose: int = 1,
    reversed=False,
):
    """
    Create a TMX for the dataset
    """

    srclang = "en"
    trglang = "fr"

    if reversed:
        tmx_file = tmxfile(None, trglang, srclang)
    else:
        tmx_file = tmxfile(None, srclang, trglang)

    for i_row, row in df.iterrows():
        if verbose >= 2:
            print(f"row {i_row}/{len(df)}")
        # print(row)

        doc_counter = row.document_counter

        # Source and target file
        base_orig = f"{doc_counter:06d}"
        filename_source = os.path.join(INPUT_FOLDER, f"{base_orig}.src")
        filename_target = os.path.join(INPUT_FOLDER, f"{base_orig}.trg")

        # Read the source and target file
        try:
            l_source = read_lines(filename_source)
            l_target = read_lines(filename_target)
        except Exception:
            print(f"Error for {filename_source} or {filename_target}")
            continue

        geo = pub_geo.get(row.publication_source.lower())

        if geo is None:
            if verbose >= 1:
                warnings.warn(
                    f"{row.document_counter} Geo not found for {row.publication_source}",
                    UserWarning,
                )
            trglang_ = trglang
        else:
            trglang_ = f"{trglang}-{geo}"

        for source, target in zip(l_source, l_target):
            if reversed:
                tmx_file.addtranslation(target, trglang_, source, srclang, comment=None)
            else:
                tmx_file.addtranslation(source, srclang, target, trglang_, comment=None)

    tmx_file.savefile(filename_tmx)
