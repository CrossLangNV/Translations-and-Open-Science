import os.path

from human_evaluation import process_tsv

DIRNAME_DATA = os.path.join(os.path.dirname(__file__), "../DATA")
assert os.path.exists(DIRNAME_DATA)

if __name__ == "__main__":
    input_file = os.path.join(DIRNAME_DATA, "sh7-dataset.tsv")
    assert os.path.exists(input_file), "Sanity check: input file does not exist"

    process_tsv.create_documents(
        input_file, outdir=os.path.join(DIRNAME_DATA, "documents"), write=False
    )
