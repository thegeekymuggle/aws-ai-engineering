# import os
# import boto3

# s3 = boto3.client("s3")          # no keys: Lambda supplies the role's temporary credentials
# BUCKET = os.environ["BUCKET"]    # bucket name comes from config, not hard-coded

# def lambda_handler(event, context):
#     key = event.get("key", "hello.txt")
#     obj = s3.get_object(Bucket=BUCKET, Key=key)
#     body = obj["Body"].read().decode("utf-8")
#     print(f"Read {len(body)} bytes from s3://{BUCKET}/{key}")
#     return {"key": key, "content": body}



import json
import os
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET"]

def respond(status, body):
    # API Gateway expects this exact shape; body must be a STRING
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

def lambda_handler(event, context):
    # ?key=hello.txt arrives here; the field is missing entirely if there's no query string
    params = event.get("queryStringParameters") or {}
    key = params.get("key", "hello.txt")

    try:
        obj = s3.get_object(Bucket=BUCKET, Key=key)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        print(json.dumps({"level": "WARN", "key": key, "error": code}))
        if code in ("NoSuchKey", "AccessDenied"):
            return respond(404, {"error": f"'{key}' not found"})
        raise  # anything unexpected -> let it fail loudly

    content = obj["Body"].read().decode("utf-8")
    print(json.dumps({"level": "INFO", "key": key, "bytes": len(content)}))
    return respond(200, {"key": key, "content": content})