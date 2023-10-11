import diff_match_patch
import numpy as np
from bleurt.score import BleurtScorer
from comet import download_model, load_from_checkpoint
from nltk.translate.meteor_score import meteor_score
from sacrebleu import BLEU, TER, CHRF


def corpus_bleu_score(references: list[str], hypotheses: list[str]) -> float:
    """
    Corpus score (single score for all sentences)
    Value between 0. and 1.
    """
    bleu = BLEU()

    corpus_bleu = bleu.corpus_score(hypotheses, [references])

    # Normalize the score
    score = corpus_bleu.score / 100

    return score


def TER_score_corpus(references: list[str], hypotheses: list[str]) -> float:
    """
    Corpus score (single score for all sentences)
    Value between 0 and 1*
        *not necessarily, but usually
    """
    ter = TER()
    corpus_ter = ter.corpus_score(hypotheses, [references])

    # Normalize the score
    score = corpus_ter.score / 100

    return score


def ChrF_score_corpus(references: list[str], hypotheses: list[str]) -> float:
    """
    Corpus score (single score for all sentences)
    Value between 0 and 1
    """
    chrf = CHRF()
    corpus_chrf = chrf.corpus_score(hypotheses, [references])

    # Normalize the score
    score = corpus_chrf.score / 100

    return score


def METEOR_score_corpus(references: list[str], hypotheses: list[str]) -> float:
    """
    Corpus score (single score for all sentences)
    Value between 0 and 1
    """

    # https://stackoverflow.com/a/67387199

    meteor_score_sentences_list = list()
    [
        meteor_score_sentences_list.append(meteor_score(expect, predict))
        for expect, predict in zip(references, hypotheses)
    ]
    meteor_score_res = np.mean(meteor_score_sentences_list)
    return meteor_score_res


def comet_score_corpus(
    sources: list[str], references: list[str], hypotheses: list[str]
) -> float:
    """
    Corpus score (single score for all sentences)
    Value between 0 and 1
    """

    model_path = download_model("Unbabel/wmt22-comet-da")
    model = load_from_checkpoint(model_path)

    data = []
    for ref, hypo, src in zip(references, hypotheses, sources):
        data.append({"src": src, "mt": hypo, "ref": ref})

    model_output = model.predict(data, batch_size=8, gpus=1)

    return model_output.system_score


def comet_sentence(
    sources: list[str], references: list[str], hypotheses: list[str]
) -> list[float]:
    """
    Sentence scores
    """

    model_path = download_model("Unbabel/wmt22-comet-da")
    model = load_from_checkpoint(model_path)

    data = []
    for ref, hypo, src in zip(references, hypotheses, sources):
        data.append({"src": src, "mt": hypo, "ref": ref})

    model_output = model.predict(data, batch_size=8, gpus=1)

    return model_output.scores


def BLEURT_sentence(references: list[str], hypotheses: list[str]) -> list[float]:
    """
    Sentence scores (score for each sentence)
    Values between 0-ish and 1-ish
    https://github.com/google-research/bleurt
    (!) Only supports English
    """

    scorer = BleurtScorer()
    scores = scorer.score(references=references, candidates=hypotheses)

    return scores


def BLEURT_corpus(references: list[str], hypotheses: list[str]) -> float:
    """
    Corpus score (single score for all sentences)
    *Average of sentence scores
    Value between 0-ish and 1-ish
    https://github.com/google-research/bleurt
    (!) Only supports English
    """

    return np.mean(BLEURT_sentence(references, hypotheses))


def sentence_bleu_scores(references: list[str], hypotheses: list[str]) -> list[float]:
    """
    Sentence score (score for each sentence)
    """
    bleu = BLEU(effective_order=True)

    sentence_bleu = [
        float(bleu.sentence_score(hypothesis, [reference]).format(score_only=True))
        / 100
        for hypothesis, reference in zip(hypotheses, references)
    ]

    return sentence_bleu


def TER_sentence(references: list[str], hypotheses: list[str]) -> list[float]:
    """
    Sentence score (score for each sentence)
    """
    ter = TER()

    # Normalize the score
    ter_sentences = [
        ter.sentence_score(hypo, [ref]).score / 100
        for ref, hypo in zip(references, hypotheses)
    ]

    return ter_sentences


def ChrF_sentence(references: list[str], hypotheses: list[str]) -> list[float]:
    """
    Sentence score (score for each sentence)
    """
    chrf = CHRF()

    # Normalize the score
    chrf_sentences = [
        chrf.sentence_score(hypo, [ref]).score / 100
        for ref, hypo in zip(references, hypotheses)
    ]

    return chrf_sentences


def sentence_dist_scores(references: list[str], hypotheses: list[str]) -> list[int]:
    """
    Sentence score (score for each sentence)
    """
    dmp = diff_match_patch.diff_match_patch()

    l = []
    for ref, hypo in zip(references, hypotheses):
        # An array of differences is computed which describe the transformation of trans_lines into ref_lines.
        # Each difference is a tuple. The first element specifies if it is an insertion (1), a deletion (-1)
        # or an equality (0). The second element specifies the affected text.
        # Output example: # Result: [(-1, "Hell"), (1, "G"), (0, "o"), (1, "odbye"), (0, " World.")]
        diff = dmp.diff_main(hypo, ref)
        dist = dmp.diff_levenshtein(diff)
        l.append(dist)

    return l
