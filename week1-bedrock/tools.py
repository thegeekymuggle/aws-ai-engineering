import sys
import boto3

MODEL_ID = "us.amazon.nova-lite-v1:0"
client = boto3.client("bedrock-runtime", region_name="us-east-1")

# --- The actual tool: plain Python, nothing to do with the model ---
FAKE_WEATHER = {
    "bengaluru": {"temp_c": 24, "condition": "light rain", "rain_chance_pct": 70},
    "mumbai":    {"temp_c": 31, "condition": "humid, cloudy", "rain_chance_pct": 30},
    "delhi":     {"temp_c": 27, "condition": "hazy sunshine", "rain_chance_pct": 5},
}

def get_weather(city: str) -> dict:
    data = FAKE_WEATHER.get(city.strip().lower())
    if data is None:
        return {"error": f"No weather data available for '{city}'."}
    return {"city": city, **data}

# --- The tool's DESCRIPTION, which is all the model ever sees ---
TOOL_CONFIG = {
    "tools": [{
        "toolSpec": {
            "name": "get_weather",
            "description": (
                "Get today's weather for an Indian city. Use this whenever the user "
                "asks about weather, rain, temperature, or what to wear or carry."
            ),
            "inputSchema": {"json": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name, e.g. Bengaluru"}
                },
                "required": ["city"],
            }},
        }
    }]
}

def run_tool(name, tool_input):
    """Our security checkpoint: validate before running anything."""
    if name != "get_weather":
        return {"error": f"Unknown tool '{name}'."}
    city = tool_input.get("city")
    if not isinstance(city, str) or not city.strip() or len(city) > 50:
        return {"error": "Invalid 'city' input."}
    return get_weather(city)


def ask(question):
    messages = [{"role": "user", "content": [{"text": question}]}]

    for step in range(1, 6):   # safety limit: never loop forever
        response = client.converse(
            modelId=MODEL_ID,
            messages=messages,
            toolConfig=TOOL_CONFIG,
            inferenceConfig={"maxTokens": 500, "temperature": 0},
        )
        msg = response["output"]["message"]
        messages.append(msg)

        if response["stopReason"] != "tool_use":
            answer = "".join(b.get("text", "") for b in msg["content"])
            print(f"\nFinal answer: {answer}")
            print(f"(total steps: {step})")
            return

        # The model asked for one or more tools: run each, collect results
        results = []
        for block in msg["content"]:
            if "toolUse" in block:
                call = block["toolUse"]
                print(f"[step {step}] model requests: {call['name']}({call['input']})")
                output = run_tool(call["name"], call["input"])
                print(f"[step {step}] our code returns: {output}")
                results.append({
                    "toolResult": {
                        "toolUseId": call["toolUseId"],   # links the result to the request
                        "content": [{"json": output}],
                    }
                })

        # Tool results go back as a USER message
        messages.append({"role": "user", "content": results})

    print("Stopped: too many tool steps.")


if __name__ == "__main__":
    ask(" ".join(sys.argv[1:]) or "Should I carry an umbrella in Bengaluru today?")