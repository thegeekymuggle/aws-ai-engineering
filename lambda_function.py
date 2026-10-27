import os
import boto3

s3 = boto3.client("s3")          # no keys: Lambda supplies the role's temporary credentials
BUCKET = os.environ["BUCKET"]    # bucket name comes from config, not hard-coded

def lambda_handler(event, context):
    key = event.get("key", "hello.txt")
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    body = obj["Body"].read().decode("utf-8")
    print(f"Read {len(body)} bytes from s3://{BUCKET}/{key}")
    return {"key": key, "content": body}