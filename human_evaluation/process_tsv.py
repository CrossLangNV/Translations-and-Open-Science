import os
import re
import sys

import pandas as pd


def read_tsv(filename, encoding="utf-8") -> pd.DataFrame:
    data = pd.read_csv(filename, sep="\t", encoding=encoding, index_col=0)

    return data


def sanity_check_all_cells_present(df: pd.DataFrame):
    # Sanity check: All cells should be present
    assert df.isnull().sum().sum() == 0, "Some cells are missing"


def sanity_check_segmentation(line):
    """
    We expect that the text was correctly segmented.
    E.g. the following should NOT occur
      - "Hello world. How are you?"
      - "Hello world.How are you?"
    :return:
        no hard errors, will print a warning if something is wrong
    """

    # Test with regex, check both with and without space

    # - "Hello world.How are you?"
    pattern = r"\.[a-zA-Z]{2,}"
    # pattern = r"([a-zA-Z0-9])\.([a-zA-Z0-9])"
    if re.search(pattern, line):
        print("Warning: Could contain unsegmented text:", line)

        return False

    # pattern = r"([a-zA-Z0-9])\. ([a-zA-Z0-9])"
    # if re.search(pattern, line):
    #     print("Warning: Could contain unsegmented text:", line)

    return True


def sanity_check_source_target_sentence_split(source, target) -> int:
    """
    We noticed that some sentences are 2 sentences in the source, but only 1 in the target (or vice versa).
    This could be due to using sub-sentences in the source, but not in the target.
    :param source:
    :param target:
    :return: 1 if there is a problem, Null otherwise

    TODO:
     - Does not work 100% of the time, e.g.:
        - To remove false positives, we skip sentences that contain a URL
    """

    # <sentence>.<sentence>, the second sentence is expected to start with a capital letter
    # - "Hello world.How are you?"
    pattern = r"[a-zA-Z]{2,}\.[A-Z][a-zA-Z]"

    # First filtering
    if re.search(pattern, source) and re.search(pattern, target):

        # Remove False positives from URL's
        if ("www" in source) or ("www" in target):
            return 0
        if ("http" in source) or ("http" in target):
            return 0

        print(
            f"Warning: Both source and target possibly not segmented correctly:\n\t{source}\n\t{target}"
        )
        return 1


def create_dir(outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir)


def create_documents(filename, outdir, write=True):
    data = read_tsv(filename)
    sanity_check_all_cells_present(data)

    create_dir(outdir)

    # fields: index,source_text,target_text,domain,disciplines,publication_type,publication_source,
    #             #         URL_source,URL_target,title_source,title_target,keywords_source,keywords_target,author,
    #             #         language_variety,publication_license,similarity_scores
    print("Fields:", ", ".join(data.keys()))

    KEY_URL_SOURCE = "URL_source"
    KEY_URL_TARGET = "URL_target"

    for key in [KEY_URL_SOURCE, KEY_URL_TARGET]:
        assert key in data, f"Field {key} not found in {filename}"

    # Group by document
    # A document is defined by the URL_source and URL_target fields
    l_key_group = [KEY_URL_SOURCE, KEY_URL_TARGET]
    n_documents = len(data.groupby(l_key_group))
    print(f"Found {n_documents} documents")

    n_warnings_segment = 0
    l_meta = []
    l_key_meta_extra = [
        "document_counter",
        "number_segments",
        "number_source_words",
        "number_target_words",
    ]
    l_key_meta = [
        key
        for key in data.keys()
        if key
           not in [
               "index",
               "source_text",
               "target_text",
               "similarity_scores",
           ]
    ]
    l_key_meta_all = l_key_meta_extra + l_key_meta

    print("Progress:")
    for i_doc, (keys, doc_group) in enumerate(data.groupby(l_key_group, sort=False)):
        # Progres bar
        print(f"Document {i_doc + 1}/{n_documents}", end="\r", flush=True)

        # Start to count from 1
        document_counter = i_doc + 1

        d_meta_extra = {
            "document_counter": document_counter,
            "number_segments": len(doc_group),
        }

        for i_line, (src, trg) in enumerate(zip(doc_group.source_text, doc_group.target_text)):
            if sanity_check_source_target_sentence_split(src, trg):
                print(
                    "Possible segmentation mistake @",
                    doc_group.iloc[i_line].URL_source,
                    doc_group.iloc[i_line].URL_target,
                )
                n_warnings_segment += 1

        for langdir in ["source", "target"]:
            key_text = langdir + "_text"
            ext = {"source": "src", "target": "trg"}[langdir]
            l_text = doc_group[key_text].tolist()

            if write:
                with open(
                        outdir + "/" + f"{document_counter:06d}.{ext}", "w", encoding="utf-8"
                ) as f:
                    f.writelines(map(lambda s: s + "\n", l_text))

            # Word count
            d_meta_extra[f"number_{langdir}_words"] = sum(
                map(lambda s: len(s.split()), l_text)
            )

        d_meta = {key: doc_group[key].iloc[0] for key in l_key_meta}

        l_meta.append({**d_meta_extra, **d_meta})

    print(f"Found {n_warnings_segment} lines with warnings")

    df_meta = pd.DataFrame(l_meta, columns=l_key_meta_all)

    if write:
        df_meta.to_excel(outdir + "/stats.xlsx", index=False)

    return df_meta


def get_field_vals(filename, fieldname):
    lines = open(filename).readlines()
    vals = dict()
    for linenum, line in zip(range(len(lines)), lines):
        fields = line.split("\t")
        if linenum == 0:
            for colid, fieldname in zip(range(len(fields)), fields):
                fieldname2colid[fieldname] = colid
        else:
            val = get_val(fields, fieldname)
            vals[val] = get(vals[val], 0) + 1
    for val in sorted(vals, key=lambda val: vals[val], reverse=True):
        print(vals[val], val)


def get_val(l_line, fieldname2colid, name):
    return l_line[fieldname2colid[name]]


if __name__ == "__main__":
    if len(sys.argv) < 4 or not sys.argv[2] in ["createdocs", "getfieldvals"]:
        print(
            "syntax: [tsv file] [createdocs] [outdir] or [tsv file] [getvalfreq] [field name]"
        )
        sys.exit()
    tsvfile, action, actionarg = sys.argv[1:4]
    if action == "createdocs":
        create_documents(tsvfile, actionarg)
    else:
        get_field_vals(tsvfile, fieldname, actionarg)
