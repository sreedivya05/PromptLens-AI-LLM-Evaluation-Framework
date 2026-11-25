import re
from collections import Counter


# =========================================================
# TOKENIZATION
# =========================================================

def tokenize(text):
    """
    Convert text into normalized word tokens.
    """

    text = str(text).lower()

    return re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text
    )


# =========================================================
# ACCURACY
# =========================================================

def word_overlap_score(
    generated,
    reference
):
    """
    Calculate basic word-overlap similarity
    between generated and reference answers.

    This is a baseline metric.
    """

    generated_tokens = tokenize(
        generated
    )

    reference_tokens = tokenize(
        reference
    )

    if not reference_tokens:
        return 0.0

    generated_counts = Counter(
        generated_tokens
    )

    reference_counts = Counter(
        reference_tokens
    )

    overlap = 0

    for word in reference_counts:

        overlap += min(
            generated_counts.get(
                word,
                0
            ),
            reference_counts[word]
        )

    score = (
        overlap /
        len(reference_tokens)
    ) * 100

    return min(
        round(score, 2),
        100
    )


# =========================================================
# RELEVANCE
# =========================================================

def relevance_score(
    output,
    input_text
):
    """
    Estimate relevance using word overlap
    between input and generated output.

    Baseline heuristic.
    """

    input_tokens = set(
        tokenize(input_text)
    )

    output_tokens = set(
        tokenize(output)
    )

    if not input_tokens:
        return 0.0

    overlap = (
        input_tokens &
        output_tokens
    )

    score = (
        len(overlap) /
        len(input_tokens)
    ) * 100

    return min(
        round(score, 2),
        100
    )


# =========================================================
# CONSISTENCY
# =========================================================

def consistency_score(output):
    """
    Basic consistency/content score.

    This currently checks whether the response
    contains meaningful content.
    """

    if not str(output).strip():
        return 0.0

    words = tokenize(output)

    if len(words) < 3:
        return 40.0

    return 100.0


# =========================================================
# CONCISENESS
# =========================================================

def conciseness_score(output):
    """
    Estimate conciseness based on output length.
    """

    words = tokenize(output)

    count = len(words)

    if count == 0:
        return 0.0

    if count <= 50:
        return 100.0

    if count <= 100:
        return 90.0

    if count <= 150:
        return 80.0

    if count <= 250:
        return 65.0

    return 50.0


# =========================================================
# HALLUCINATION RISK
# =========================================================

def hallucination_risk(
    output,
    expected
):
    """
    Estimate unsupported content against
    the expected/reference answer.

    This is a baseline heuristic,
    not a true hallucination detector.
    """

    if not expected.strip():
        return 0.0

    output_tokens = set(
        tokenize(output)
    )

    expected_tokens = set(
        tokenize(expected)
    )

    if not output_tokens:
        return 100.0

    unsupported = (
        output_tokens -
        expected_tokens
    )

    risk = (
        len(unsupported) /
        len(output_tokens)
    ) * 100

    return min(
        round(risk, 2),
        100
    )


# =========================================================
# COMPLETE EVALUATION
# =========================================================

def evaluate_output(
    output,
    expected,
    input_text
):
    """
    Evaluate a generated LLM response.
    """

    output = str(output)
    expected = str(expected)
    input_text = str(input_text)

    # -----------------------------------------------------
    # ACCURACY
    # -----------------------------------------------------

    if expected.strip():

        accuracy = word_overlap_score(
            output,
            expected
        )

    else:

        accuracy = 0.0

    # -----------------------------------------------------
    # RELEVANCE
    # -----------------------------------------------------

    relevance = relevance_score(
        output,
        input_text
    )

    # -----------------------------------------------------
    # CONSISTENCY
    # -----------------------------------------------------

    consistency = consistency_score(
        output
    )

    # -----------------------------------------------------
    # CONCISENESS
    # -----------------------------------------------------

    conciseness = conciseness_score(
        output
    )

    # -----------------------------------------------------
    # HALLUCINATION RISK
    # -----------------------------------------------------

    hallucination = hallucination_risk(
        output,
        expected
    )

    # -----------------------------------------------------
    # HALLUCINATION SAFETY
    # -----------------------------------------------------

    hallucination_safety = (
        100 - hallucination
    )

    # -----------------------------------------------------
    # OVERALL SCORE
    # -----------------------------------------------------

    quality_score = (
        accuracy * 0.30
        + relevance * 0.25
        + consistency * 0.15
        + conciseness * 0.15
        + hallucination_safety * 0.15
    )

    quality_score = round(
        quality_score,
        2
    )

    return {
        "accuracy": round(
            accuracy,
            2
        ),

        "relevance": round(
            relevance,
            2
        ),

        "consistency": round(
            consistency,
            2
        ),

        "conciseness": round(
            conciseness,
            2
        ),

        "hallucination_risk": round(
            hallucination,
            2
        ),

        "quality_score": quality_score
    }