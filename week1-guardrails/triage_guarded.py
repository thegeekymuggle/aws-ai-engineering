import json

from compare import SYSTEM_PROMPT, parse_output, client    # reuse Day 4 code
from test_guardrail import check

MODEL_ID = "us.amazon.nova-micro-v1:0"


def triage(ticket_text):
    # Layer 1: guardrail on the untrusted input
    outcome, hits, safe_text, _ = check(ticket_text)
    if outcome == "BLOCK":
        # Don't drop the customer: route to a human with the reason attached
        return {"status": "manual_review", "needs_human": True, "guardrail": hits}

    # Layer 2: the model only ever sees the (possibly masked) text
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": f"Ticket:\n{safe_text}"}]}],
        inferenceConfig={"maxTokens": 400, "temperature": 0},
    )
    text = "".join(b.get("text", "") for b in response["output"]["message"]["content"])

    # Layer 3: validate the output before trusting it
    data, error, _ = parse_output(text)
    if data is None:
        return {"status": "manual_review", "needs_human": True, "error": error}

    data["status"] = "auto_triaged"
    if outcome == "MASK":
        data["pii_masked"] = hits
    return data


if __name__ == "__main__":
    tickets = json.load(open("tickets.json", encoding="utf-8"))
    extra = [
        {"id": "P01", "text": "Refund of Rs 499 failed. Call me at 9876543210, it's urgent."},
        {"id": "P02", "text": "KYC keeps failing. My PAN is ABCPE1234F and Aadhaar is 1234 5678 9012."},
        {"id": "D01", "text": "Got my refund finally. Should I invest it in Bitcoin?"},
    ]
    for t in tickets + extra:
        result = triage(t["text"])
        print(f"\n{t['id']}: {json.dumps(result, ensure_ascii=False)}")