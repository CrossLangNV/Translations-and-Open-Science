import math


def split_sub(l: list, n_desired_min: int, n_thresh: int = None) -> list[list]:
    """
    We want to further split paragraphs into subparagraphs to make them shorter.
    If the paragraph is more than n_max sentences, we split it into subparagraphs of length N_min <= N <= N_max.
    Given a list (of e.g. se
    :param l: List (of sentences)
    :param n_thresh: max length of a paragraph can have before we start to split it
        (!) if len(l) == n_thresh, we don't split it !
    :param n_desired_min: min length of each subparagraph
    :return:
    """

    if n_thresh:
        assert n_thresh >= n_desired_min

        if len(l) <= n_thresh:
            # If the paragraph is short enough, we don't split it
            return [l]

    n_l = len(l)
    n_sub = n_l // n_desired_min
    avg_length = n_l / n_sub

    l_split = []
    for i in range(n_sub):
        # We split the paragraph into n_sub paragraphs of length n_max

        i_0 = math.ceil(i * avg_length)
        i_1 = math.ceil((i + 1) * avg_length)

        l_split.append(l[i_0:i_1])

    return l_split
