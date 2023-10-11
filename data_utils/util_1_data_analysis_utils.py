import pandas as pd
from sklearn.model_selection import train_test_split


l_open_licences = [
    # Discipline 1:
    "CC BY-SA-4.0",
    "CC BY-4.0",
    "CC BY-NC-4.0",
    "CC BY-NC-SA-4.0",
    # Discipline 2:
    "CC BY-ND 4.0",
    "https://creativecommons.org/licenses/by/4.0/",
    "https://creativecommons.org/licenses/by-nc-nd/4.0/",
    "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    "Free Access",
    "Open access",
    # Discipline 3:
    "https://creativecommons.org/licenses/by-nc/4.0",
    "http://creativecommons.org/licenses/by-nc/4.0",
]
l_open_licences = [x.lower() for x in l_open_licences]

KEY_PUBLICATION_JOURNAL_ARTICLE = "journal article"
KEY_PUBLICATION_THESIS_ABSTRACT = "thesis abstract"


def split_n_segments(
    df: pd.DataFrame, n_target_segments: int, random_state: int = 42, name: str = ""
):
    """
    Split the dataframe into two dataframes, with the first one having around <n_segments> segments
    :param df:
    :param n_target_segments:
    :return: train_df_i, test_df_i
    """

    if len(df) == 1:
        print(
            "WARNING: len(df_type) == 1. Adding all to training and none to test set."
        )
        return df, None
    if len(df) == 0:
        print("WARNING: len(df_type) == 0. Nothing to split")
        return None, None

    n = df.number_segments.count()
    n_segm = df.number_segments.sum()

    r = n_target_segments / n_segm

    n_doc_test = round(n * r)
    print(f"Type: {name}, n_tot: {n}, n_test: {n_doc_test}, r: {r}")

    if r <= 0:
        print("WARNING: r <= 0. Adding all to training and none to test set.")
        return df, None
    elif r >= 1:
        print("WARNING: r >= 1. Adding all to test and none to training set.")
        return None, df

    else:
        return train_test_split(df, test_size=r, random_state=random_state)


def split_open_licences(
    df: pd.DataFrame,
    keys_publication_type: str,
    max_segments_pub_type: int = None,
):
    # Filter the dataframe to only include the open licences
    f = df.publication_license.str.lower().isin(l_open_licences)

    df_open_licences = df[f]
    df_not_open_licences = df[~f]

    if not max_segments_pub_type:
        return df_open_licences, df_not_open_licences

    # Else cap the number of segments per publication type
    l_df_open = []
    l_df_not_open = [df_not_open_licences]

    for pub_type in keys_publication_type:
        df_open_pub = df_open_licences[df_open_licences.publication_type == pub_type]

        if isinstance(max_segments_pub_type, dict):
            n = max_segments_pub_type.get(pub_type, max_segments_pub_type[None])
        else:
            n = max_segments_pub_type

        df_not_open_i, df_open_i = split_n_segments(
            df_open_pub, n, name="Open licences" + pub_type
        )

        if df_open_i is not None:
            l_df_open.append(df_open_i)
        if df_not_open_i is not None:
            l_df_not_open.append(df_not_open_i)

    # Update the dataframes
    df_open_licences = pd.concat(l_df_open)
    df_not_open_licences = pd.concat(l_df_not_open)
    return df_open_licences, df_not_open_licences


def split_equal_publication_type(
    df: pd.DataFrame,
    n_tgt_segm: int = 1000,
    n_journal_articles: int = None,
    n_thesis_abstracts: int = None,
    n_max_segments_pub_type: dict = dict(),
    random_state: int = 42,
):
    """
    :param df:
    :param n_tgt_segm: For each type of publication, we want to have around <n> segments in the test set
    :param n_journal_articles: (Optional) if available, override the number of journal articles to include in the test set
    :return:
    """

    l_train_df = []
    l_test_df = []
    print("Aim: n_test_segm = ", n_tgt_segm)
    for publication_type in df.publication_type.unique():
        df_type = df[df.publication_type == publication_type]

        n_segments = n_tgt_segm
        # Check to override n_segments
        if publication_type == KEY_PUBLICATION_JOURNAL_ARTICLE:
            if n_journal_articles is not None:
                print("Make exception for journal articles:")
                n_segments = n_journal_articles
        elif publication_type == KEY_PUBLICATION_THESIS_ABSTRACT:
            if n_thesis_abstracts is not None:
                print("Make exception for thesis abstracts:")
                n_segments = n_thesis_abstracts

        if publication_type in n_max_segments_pub_type:
            n_segments = n_max_segments_pub_type[publication_type]
        train_df_i, test_df_i = split_n_segments(
            df_type,
            n_target_segments=n_segments,
            random_state=random_state,
            name=publication_type,
        )

        if train_df_i is not None:
            l_train_df.append(train_df_i)
        if test_df_i is not None:
            l_test_df.append(test_df_i)
        # df.loc[df_type.index, "test_set"] = test_df.index
    train_df = pd.concat(l_train_df)
    test_df = pd.concat(l_test_df)

    return train_df, test_df
