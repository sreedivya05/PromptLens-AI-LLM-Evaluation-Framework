# LLM Prompt Evaluation & Optimization Framework

A portfolio project for evaluating LLM prompts systematically rather than judging outputs manually.

## Core flow

Test Cases + Prompt Variants
→ LLM Execution
→ Quality Evaluation
→ Metric Aggregation
→ Prompt Comparison
→ Winner / Recommendation

## Metrics

- Accuracy
- Relevance
- Consistency
- Conciseness
- Hallucination Risk
- Latency
- Overall Quality Score

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Demo Mode works without an API key.

For live evaluation:
1. Copy `.env.example` to `.env`
2. Add `OPENAI_API_KEY`
3. Select OpenAI API in the sidebar
4. Run evaluation

## Dataset structure

Test case CSV:
- test_id
- input
- expected

Prompt variant CSV:
- prompt_id
- prompt_name
- prompt_template

The `{input}` placeholder is replaced with each test case input.
