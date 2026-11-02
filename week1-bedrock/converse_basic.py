import sys
import boto3

MODEL_ID = "us.amazon.nova-lite-v1:0"
client = boto3.client("bedrock-runtime", region_name="us-east-1")


def ask(question, max_tokens=300, temperature=0.3):
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": "You are a concise AWS tutor. Answer in at most 3 sentences."}],
        messages=[{"role": "user", "content": [{"text": question}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
    )

    text = response["output"]["message"]["content"][0]["text"]
    print(text)
    print("-" * 40)
    print("stopReason:", response["stopReason"])
    print("usage:     ", response["usage"])
    print("latencyMs: ", response["metrics"]["latencyMs"])


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What is AWS Lambda?"
    ask(question)