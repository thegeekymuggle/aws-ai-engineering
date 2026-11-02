import boto3

MODEL_ID = "us.amazon.nova-lite-v1:0"
client = boto3.client("bedrock-runtime", region_name="us-east-1")

SYSTEM = [{"text": "You are a friendly assistant. Keep answers short."}]
history = []   # this list IS the conversation memory

print("Chat started. Type 'exit' to quit.")
while True:
    user_text = input("\nYou: ").strip()
    if user_text.lower() in ("exit", "quit"):
        break

    history.append({"role": "user", "content": [{"text": user_text}]})

    response = client.converse(
        modelId=MODEL_ID,
        system=SYSTEM,
        messages=history,                       # the WHOLE history, every time
        inferenceConfig={"maxTokens": 400},
    )

    reply = response["output"]["message"]       # already {"role": "assistant", "content": [...]}
    history.append(reply)
    print("Bot:", reply["content"][0]["text"])

    u = response["usage"]
    print(f"   [input {u['inputTokens']} | output {u['outputTokens']} | messages sent: {len(history) - 1}]")