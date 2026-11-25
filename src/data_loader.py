import pandas as pd


def load_test_cases(file):
    """
    Load test cases from an uploaded CSV file.

    Required column:
        input

    Recommended columns:
        test_id
        input
        expected

    Optional:
        category
    """

    # Reset file position
    file.seek(0)

    df = pd.read_csv(file)

    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # -----------------------------------------------------
    # VALIDATE REQUIRED COLUMN
    # -----------------------------------------------------

    if "input" not in df.columns:

        raise ValueError(
            "Test Cases CSV must contain an 'input' column."
        )

    # -----------------------------------------------------
    # CREATE TEST ID IF MISSING
    # -----------------------------------------------------

    if "test_id" not in df.columns:

        df.insert(
            0,
            "test_id",
            [
                f"TC{i + 1:03d}"
                for i in range(len(df))
            ]
        )

    # -----------------------------------------------------
    # CREATE EXPECTED COLUMN IF MISSING
    # -----------------------------------------------------

    if "expected" not in df.columns:

        df["expected"] = ""

    # -----------------------------------------------------
    # REMOVE EMPTY INPUT ROWS
    # -----------------------------------------------------

    df = df.dropna(
        subset=["input"]
    ).reset_index(drop=True)

    # -----------------------------------------------------
    # CLEAN DATA TYPES
    # -----------------------------------------------------

    df["test_id"] = (
        df["test_id"]
        .fillna("")
        .astype(str)
    )

    df["input"] = (
        df["input"]
        .fillna("")
        .astype(str)
    )

    df["expected"] = (
        df["expected"]
        .fillna("")
        .astype(str)
    )

    # -----------------------------------------------------
    # VALIDATE NON-EMPTY INPUT
    # -----------------------------------------------------

    if df["input"].str.strip().eq("").all():

        raise ValueError(
            "The Test Cases CSV contains no valid input values."
        )

    return df


def load_prompt_variants(file):
    """
    Load prompt variants from an uploaded CSV file.

    Required column:
        prompt_template

    Recommended columns:
        prompt_id
        prompt_name
        prompt_template
    """

    # Reset file position
    file.seek(0)

    df = pd.read_csv(file)

    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # -----------------------------------------------------
    # VALIDATE REQUIRED COLUMN
    # -----------------------------------------------------

    if "prompt_template" not in df.columns:

        raise ValueError(
            "Prompt Variants CSV must contain "
            "a 'prompt_template' column."
        )

    # -----------------------------------------------------
    # CREATE PROMPT ID IF MISSING
    # -----------------------------------------------------

    if "prompt_id" not in df.columns:

        df.insert(
            0,
            "prompt_id",
            [
                f"P{i + 1:03d}"
                for i in range(len(df))
            ]
        )

    # -----------------------------------------------------
    # CREATE PROMPT NAME IF MISSING
    # -----------------------------------------------------

    if "prompt_name" not in df.columns:

        df["prompt_name"] = (
            "Prompt "
            + df["prompt_id"].astype(str)
        )

    # -----------------------------------------------------
    # REMOVE EMPTY PROMPTS
    # -----------------------------------------------------

    df = df.dropna(
        subset=["prompt_template"]
    ).reset_index(drop=True)

    # -----------------------------------------------------
    # CLEAN DATA
    # -----------------------------------------------------

    df["prompt_id"] = (
        df["prompt_id"]
        .fillna("")
        .astype(str)
    )

    df["prompt_name"] = (
        df["prompt_name"]
        .fillna("")
        .astype(str)
    )

    df["prompt_template"] = (
        df["prompt_template"]
        .fillna("")
        .astype(str)
    )

    # -----------------------------------------------------
    # VALIDATE PROMPT CONTENT
    # -----------------------------------------------------

    if df["prompt_template"].str.strip().eq("").all():

        raise ValueError(
            "The Prompt Variants CSV contains no valid "
            "prompt templates."
        )

    # -----------------------------------------------------
    # VALIDATE {input}
    # -----------------------------------------------------

    invalid_prompts = df[
        ~df["prompt_template"].str.contains(
            r"\{input\}",
            regex=True,
            na=False
        )
    ]

    if not invalid_prompts.empty:

        invalid_names = (
            invalid_prompts["prompt_name"]
            .tolist()
        )

        raise ValueError(
            "Every prompt_template must contain "
            "'{input}'. Invalid prompts: "
            + ", ".join(invalid_names)
        )

    return df