
import os
import time


def run_llm(
    prompt,
    provider="Demo Mode",
    model="gpt-4o-mini",
    expected=""
):
    """
    Generate an LLM response and return output and latency.
    """

    start_time = time.time()

    if provider == "Demo Mode":
        output = demo_response(prompt)
        return output, time.time() - start_time

    if provider == "OpenAI API":

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured. "
                "Add it to your .env file."
            )

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional customer support "
                            "representative. Write clear, empathetic, "
                            "accurate and actionable responses. "
                            "Respond directly to the customer's issue. "
                            "Never repeat evaluation instructions."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )

            output = response.choices[0].message.content

            if not output:
                raise ValueError("The model returned an empty response.")

            return output.strip(), time.time() - start_time

        except ImportError:
            raise ImportError(
                "OpenAI package is not installed. "
                "Run: pip install openai"
            )

    raise ValueError(f"Unsupported provider: {provider}")


def demo_response(prompt):
    """
    Sample responses for testing the UI without an API key.
    This is NOT real LLM generation.
    """

    text = prompt.lower()

    if "payment" in text and ("failed" in text or "deducted" in text):
        return (
            "I'm sorry your payment didn't go through. "
            "Please check your bank statement and transaction status. "
            "If the amount was deducted, it may be automatically "
            "refunded within your bank's processing time. "
            "If it hasn't arrived, contact our support team with "
            "your transaction ID so we can investigate."
        )

    if "double" in text or "twice" in text:
        return (
            "I'm sorry you were charged twice. Please check your "
            "bank statement for both transactions and share the "
            "transaction details with our support team. "
            "We'll help investigate the duplicate charge."
        )

    if "refund" in text:
        return (
            "I understand you're waiting for your refund. "
            "Please check the refund status and your original "
            "payment method. If the expected processing time has "
            "passed, contact our support team with your order ID."
        )

    if "login" in text or "password" in text:
        return (
            "Sorry you're having trouble accessing your account. "
            "Please try resetting your password, check your "
            "internet connection, and attempt to log in again. "
            "If the issue continues, contact our support team."
        )

    if "order" in text and ("delivered" in text or "received" in text):
        return (
            "I'm sorry you haven't received your order. "
            "Please check your delivery location and contact "
            "our support team with your order ID so we can "
            "investigate the delivery status."
        )

    return (
        "Thank you for bringing this to our attention. "
        "We understand your concern. Please share your order "
        "or transaction details with our support team so we "
        "can investigate and help resolve the issue."
    )
