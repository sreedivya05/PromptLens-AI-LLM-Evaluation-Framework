import os
import io
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.data_loader import load_test_cases, load_prompt_variants
from src.llm_client import run_llm
from src.evaluator import evaluate_output
from src.report import build_summary


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

st.set_page_config(
    page_title="PromptLens AI",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PROMPTLENS AI UI
# =========================================================

st.title("🧪 PromptLens AI")
st.caption("AI Evaluation Platform")
st.write("Evaluate, compare, and optimize LLM prompts using repeatable test cases and quality metrics.")
st.divider()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.title("🧪 PromptLens AI")
    st.caption("LLM Prompt Evaluation Framework")
    st.subheader("Evaluation Settings")

    provider = st.selectbox(
        "LLM Provider",
        ["Demo Mode", "OpenAI API"]
    )

    model = st.text_input(
        "Model",
        os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    )

    if provider == "Demo Mode":
        st.info(
            "Demo Mode does not require an API key. "
            "Use it to test the evaluation pipeline."
        )
    else:
        st.info(
            "OpenAI API mode uses a real LLM. "
            "Make sure OPENAI_API_KEY is configured."
        )

# =========================================================
# EVALUATION WORKSPACE
# =========================================================

st.subheader("📂 Upload Evaluation Data")
st.caption("Upload your test cases and prompt variants. Each prompt will be evaluated against the same test set.")

pipeline = st.columns(5)
pipeline_data = [
    ("📁", "Upload"),
    ("🧩", "Apply Prompts"),
    ("🤖", "Generate"),
    ("📊", "Evaluate"),
    ("🏆", "Best Prompt"),
]
for col, (icon, label) in zip(pipeline, pipeline_data):
    with col:
        st.markdown(f"### {icon}")
        st.caption(label)

st.divider()

upload_col1, upload_col2 = st.columns(2)

with upload_col1:
    st.markdown("### 📋 Test Cases")
    st.write("Upload the questions or inputs that every prompt will be tested against.")
    st.caption("Required: `input`  |  Recommended: `test_id`, `expected`")

    test_file = st.file_uploader(
        "Upload Test Cases CSV",
        type=["csv"],
        key="test_cases_upload",
        help="CSV containing your evaluation test cases."
    )

with upload_col2:
    st.markdown("### 🧩 Prompt Variants")
    st.write("Upload different prompt versions that you want to compare.")
    st.caption("Required: `prompt_template`  |  Template must contain `{input}`")

    prompt_file = st.file_uploader(
        "Upload Prompt Variants CSV",
        type=["csv"],
        key="prompt_variants_upload",
        help="CSV containing the prompts to compare."
    )

status_col1, status_col2 = st.columns(2)

with status_col1:
    if test_file:
        st.success("✓ Test data ready")
        st.caption(test_file.name)
    else:
        st.warning("Waiting for test data")

with status_col2:
    if prompt_file:
        st.success("✓ Prompts ready")
        st.caption(prompt_file.name)
    else:
        st.warning("Waiting for prompts")

st.write("")

run_button = st.button(
    "▶ Run Prompt Evaluation",
    type="primary",
    use_container_width=True
)

if run_button:

    if test_file is None:

        st.error(
            "Please upload a Test Cases CSV."
        )

        st.stop()

    if prompt_file is None:

        st.error(
            "Please upload a Prompt Variants CSV."
        )

        st.stop()

    # Fresh streams
    test_data = io.BytesIO(
        test_file.getvalue()
    )

    prompt_data = io.BytesIO(
        prompt_file.getvalue()
    )

    try:

        cases = load_test_cases(
            test_data
        )

        prompts = load_prompt_variants(
            prompt_data
        )

    except Exception as e:

        st.error(
            f"Could not load uploaded files: {e}"
        )

        st.stop()

    if cases.empty:

        st.error(
            "The Test Cases CSV contains no usable rows."
        )

        st.stop()

    if prompts.empty:

        st.error(
            "The Prompt Variants CSV contains no usable rows."
        )

        st.stop()

    total_runs = (
        len(cases) *
        len(prompts)
    )

    st.success(
        f"Loaded {len(cases)} test cases × "
        f"{len(prompts)} prompts = "
        f"{total_runs} evaluation runs."
    )

    # -------------------------------------------------
    # PREVIEW
    # -------------------------------------------------

    with st.expander(
        "👀 Preview Uploaded Data"
    ):

        st.write("### Test Cases")

        st.dataframe(
            cases.head(10),
            use_container_width=True
        )

        st.write("### Prompt Variants")

        st.dataframe(
            prompts.head(10),
            use_container_width=True
        )

    # -------------------------------------------------
    # RUN EVALUATION
    # -------------------------------------------------

    st.subheader("⚙️ Running Evaluation")

    rows = []

    progress = st.progress(0)

    status = st.empty()

    completed = 0

    for _, case in cases.iterrows():

        for _, prompt in prompts.iterrows():

            test_id = str(
                case.get(
                    "test_id",
                    f"TC-{completed + 1}"
                )
            )

            prompt_id = str(
                prompt.get(
                    "prompt_id",
                    f"P-{completed + 1}"
                )
            )

            prompt_name = str(
                prompt.get(
                    "prompt_name",
                    prompt_id
                )
            )

            input_text = str(
                case.get(
                    "input",
                    ""
                )
            )

            expected = str(
                case.get(
                    "expected",
                    ""
                )
            )

            prompt_template = str(
                prompt.get(
                    "prompt_template",
                    ""
                )
            )

            rendered_prompt = (
                prompt_template.replace(
                    "{input}",
                    input_text
                )
            )

            status.markdown(
                f"""
                **Evaluating:** `{prompt_name}`  
                **Test case:** `{test_id}`
                """
            )

            try:

                output, latency = run_llm(
                    rendered_prompt,
                    provider=provider,
                    model=model,
                    expected=expected
                )

            except Exception as e:

                output = (
                    f"LLM Error: {str(e)}"
                )

                latency = 0

            try:

                metrics = evaluate_output(
                    output=output,
                    expected=expected,
                    input_text=input_text
                )

            except Exception:

                metrics = {
                    "accuracy": 0,
                    "relevance": 0,
                    "consistency": 0,
                    "conciseness": 0,
                    "hallucination_risk": 100,
                    "quality_score": 0
                }

            rows.append(
                {
                    "test_id": test_id,
                    "prompt_id": prompt_id,
                    "prompt_name": prompt_name,
                    "input": input_text,
                    "output": output,
                    "accuracy": metrics["accuracy"],
                    "relevance": metrics["relevance"],
                    "consistency": metrics["consistency"],
                    "conciseness": metrics["conciseness"],
                    "hallucination_risk": metrics[
                        "hallucination_risk"
                    ],
                    "quality_score": metrics[
                        "quality_score"
                    ],
                    "latency_sec": latency
                }
            )

            completed += 1

            progress.progress(
                completed / total_runs
            )

    status.success(
        "Evaluation completed successfully."
    )

    st.session_state["results"] = pd.DataFrame(
        rows
    )

# =====================================================
# RESULTS
# =====================================================

if "results" in st.session_state:

    results = st.session_state["results"]

    st.subheader("📊 Evaluation Results")

    try:

        summary = build_summary(
            results
        )

    except Exception as e:

        st.error(
            f"Could not build summary: {e}"
        )

        st.stop()

    if summary.empty:

        st.warning(
            "No results available."
        )

        st.stop()

    winner = summary.iloc[0]

    # -------------------------------------------------
    # KPI CARDS
    # -------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("🏆 Best Prompt", str(winner["prompt_name"]))
        st.caption("Highest overall performance")

    with c2:
        st.metric("Overall Score", f"{winner['quality_score']:.1f}/100")
        st.caption("Weighted quality score")

    with c3:
        st.metric("Average Latency", f"{winner['latency_sec']:.2f}s")
        st.caption("Average response time")

    with c4:
        st.metric("Evaluation Runs", len(results))
        st.caption("Total prompt × test combinations")
    # -------------------------------------------------
    # WINNER
    # -------------------------------------------------

    st.success(
        f"🏆 Recommended Prompt: {winner['prompt_name']}\n\n"
        f"Overall quality score: {winner['quality_score']:.1f}/100  •  "
        f"Average latency: {winner['latency_sec']:.2f}s"
    )

    # -------------------------------------------------
    # COMPARISON
    # -------------------------------------------------

    st.markdown(
        "### ⚖️ Prompt Comparison"
    )

    st.dataframe(
        summary,
        use_container_width=True
    )

    # -------------------------------------------------
    # DETAILED RESULTS
    # -------------------------------------------------

    st.markdown(
        "### 🔍 Detailed Evaluation"
    )

    detailed_columns = [
        "test_id",
        "prompt_name",
        "accuracy",
        "relevance",
        "consistency",
        "conciseness",
        "hallucination_risk",
        "quality_score",
        "latency_sec"
    ]

    detailed_columns = [
        col
        for col in detailed_columns
        if col in results.columns
    ]

    st.dataframe(
        results[detailed_columns],
        use_container_width=True
    )

    # -------------------------------------------------
    # OUTPUTS
    # -------------------------------------------------

    st.markdown(
        "### 💬 Generated Responses"
    )

    output_columns = [
        "test_id",
        "prompt_name",
        "input",
        "output"
    ]

    output_columns = [
        col
        for col in output_columns
        if col in results.columns
    ]

    st.dataframe(
        results[output_columns],
        use_container_width=True
    )

    # -------------------------------------------------
    # DOWNLOAD
    # -------------------------------------------------

    csv = results.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Full Evaluation Report",
        csv,
        "llm_evaluation_results.csv",
        "text/csv",
        use_container_width=True
    )