import pandas as pd


def build_summary(results):
    """
    Aggregate test-level results into
    prompt-level performance.
    """

    if results is None:
        return pd.DataFrame()

    if results.empty:
        return pd.DataFrame()

    summary = (
        results
        .groupby(
            [
                "prompt_id",
                "prompt_name"
            ],
            as_index=False
        )
        .agg(
            accuracy=(
                "accuracy",
                "mean"
            ),

            relevance=(
                "relevance",
                "mean"
            ),

            consistency=(
                "consistency",
                "mean"
            ),

            conciseness=(
                "conciseness",
                "mean"
            ),

            hallucination_risk=(
                "hallucination_risk",
                "mean"
            ),

            quality_score=(
                "quality_score",
                "mean"
            ),

            latency_sec=(
                "latency_sec",
                "mean"
            )
        )
    )

    # -----------------------------------------------------
    # ROUND NUMBERS
    # -----------------------------------------------------

    numeric_columns = [
        "accuracy",
        "relevance",
        "consistency",
        "conciseness",
        "hallucination_risk",
        "quality_score",
        "latency_sec"
    ]

    for column in numeric_columns:

        if column in summary.columns:

            summary[column] = (
                summary[column]
                .round(2)
            )

    # -----------------------------------------------------
    # SORT BY QUALITY SCORE
    # -----------------------------------------------------

    summary = (
        summary
        .sort_values(
            by="quality_score",
            ascending=False
        )
        .reset_index(drop=True)
    )

    return summary


def build_test_results(results):
    """
    Return detailed evaluation results.
    """

    if results is None:
        return pd.DataFrame()

    return results.copy()