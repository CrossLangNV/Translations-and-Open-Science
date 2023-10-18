import numpy as np
from scipy.stats import linregress
from sklearn.metrics import cohen_kappa_score as _cohen_kappa_score


def correlation(x: list, y: list) -> float:
    """
    Calculate the Pearson Correlation Coefficient between two list of scores,
    >> R = correlation(x, y)
    """

    slope, intercept, r_value, p_value, std_err = linregress(x, y)

    return r_value


def correlation2(x: list, y: list) -> float:
    """
    Calculate the Pearson Correlation Coefficient between two list of scores,
    >> R = correlation2(x, y)
    """

    C = np.corrcoef(x, y)

    return C[0, 1]

def cohen_kappa_score(x_scores, y_scores, labels=[1, 2, 3, 4, 5]):
    """
    Calculate the Cohen's kappa score between two list of scores.
    Assumes the scores are integers between 1 and 5.
    """

    return _cohen_kappa_score(x_scores, y_scores, labels=labels)



