import sys
import time
import boto3

MODEL_ID = "us.amazon.nova-lite-v1:0"
client = boto3.client("bedrock-runtime", region_name="us-east-1")

question = " ".join(sys.argv[1:]) or "Explain how AWS Lambda, API Gateway and S3 work together, in about 200 words."

start = time.perf_counter()
first_token_at = None
stop_reason, usage = None, None

response = client.converse_stream(
    modelId=MODEL_ID,
    messages=[{"role": "user", "content": [{"text": question}]}],
    inferenceConfig={"maxTokens": 600},
)

for event in response["stream"]:
    if "contentBlockDelta" in event:
        chunk = event["contentBlockDelta"]["delta"].get("text", "")
        if first_token_at is None:
            first_token_at = time.perf_counter()
        print(chunk, end="", flush=True)        # flush = show it immediately
    elif "messageStop" in event:
        stop_reason = event["messageStop"]["stopReason"]
    elif "metadata" in event:
        usage = event["metadata"]["usage"]

end = time.perf_counter()
print("\n" + "-" * 40)
print(f"Time to first token: {(first_token_at - start) * 1000:.0f} ms")
print(f"Total time:          {(end - start) * 1000:.0f} ms")
print(f"stopReason: {stop_reason} | usage: {usage}")