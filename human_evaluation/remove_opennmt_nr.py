import os.path
import re


def main(folder, rename=True):
    """
    OpenNMT seems to add a number to the generated translation file. This script will rename it again to the original name.
    e.g. "000058_sh03_11.en" > "1150-000058_sh03_11.en"
    """

    assert os.path.exists(folder), f"Folder {folder} does not exist"

    for filename in os.listdir(folder):
        # Check if of format "xxxx-<original_name>.<extension>"
        pattern = "^[0-9]{4}-.+[.].+$"
        if re.match(pattern, filename):
            # Rename file
            old_path = os.path.join(folder, filename)
            new_path = os.path.join(folder, filename.split("-", 1)[1])
            if rename:
                print(f"Renamed {old_path} to {new_path}")
                os.rename(old_path, new_path)

    return


if __name__ == "__main__":
    FOLDER = r"../DATA/Discipline 1 Mobility/Eval_outputs_SH7/OPERAS_SH7_Eval-OpenNMT_OPERAS_SciPar/ANR"

    main(FOLDER)
