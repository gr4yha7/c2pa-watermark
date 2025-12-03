import json
import sys
import base64
from openai import OpenAI
from watermark import watermark_image

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
# model = "gemma-3-270m-it"
model = "qwen/qwen3-vl-4b"

tools = [
    {
        "type": "function",
        "function": {
            "name": "watermark_image",
            "description": "Watermark an image with a random watermark ID. Call this whenever you need to watermark an image.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base64_image": {
                        "type": "string",
                        "description": "The base64 encoded image to watermark.",
                    },
                },
                "required": ["base64_image"],
                "additionalProperties": False,
            },
        },
    }
]
base_64_image = "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"
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant that watermarks images. Use the supplied tools to watermark images, do NOT try to process the base64_image data, just pass it to the watermark_image tool.",
    },
    {
        "role": "user",
        "content": "Watermark the following image: " + base_64_image,
    },
]

# LM Studio
try:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
    )
except Exception as e:
    print(f"Error: Failed to connect to LM Studio API at http://localhost:1234/v1", file=sys.stderr)
    print(f"Details: {e}", file=sys.stderr)
    print(f"\nMake sure LM Studio is running and the API server is enabled on port 1234.", file=sys.stderr)
    sys.exit(1)

print("\nModel response requesting tool call:\n", flush=True)
print(f"Tool call function: {response.choices[0].message.tool_calls[0].function.name if response.choices and response.choices[0].message.tool_calls else 'None'}", flush=True)

# Extract the arguments for watermark_image
# Note this code assumes we have already determined that the model generated a function call.
try:
    if not response.choices or not response.choices[0].message.tool_calls:
        print("Error: Model did not generate a tool call", file=sys.stderr)
        sys.exit(1)
    
    tool_call = response.choices[0].message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
except (IndexError, KeyError, json.JSONDecodeError) as e:
    print(f"Error: Failed to parse tool call response: {e}", file=sys.stderr)
    sys.exit(1)

# Try to get base64_image, handling potential typos in the model's response
base64_image = arguments.get("base64_image")
if not base64_image:
    # Try common variations/typos
    for key in arguments.keys():
        if "base" in key.lower() and "image" in key.lower():
            base64_image = arguments.get(key)
            print(f"Warning: Using '{key}' instead of 'base64_image'", file=sys.stderr)
            break

# Validate the base64 string
def is_valid_base64(s):
    """Check if a string is valid base64 and can be decoded."""
    if not s:
        return False
    try:
        # Try to decode it
        decoded = base64.b64decode(s, validate=True)
        return len(decoded) > 0
    except Exception:
        return False

# Validate the extracted image, or use the original if invalid
if base64_image and is_valid_base64(base64_image):
    print(f"Using base64 image from model response (length: {len(base64_image)} chars)", flush=True)
else:
    if base64_image:
        print(f"Warning: Model returned invalid base64 string (length: {len(base64_image)} chars). Using original image.", file=sys.stderr)
    else:
        print("Warning: Could not extract base64_image from tool call arguments. Using original image from message.", file=sys.stderr)
    base64_image = base_64_image

if not base64_image:
    print("Error: No base64 image available to watermark", file=sys.stderr)
    sys.exit(1)

# Call the watermark_image function with the validated base64_image
print(f"\nWatermarking image (length: {len(base64_image)} chars)...", flush=True)
wm_base64_img = watermark_image(base64_image)

if not wm_base64_img:
    print("Error: Watermarking failed", file=sys.stderr)
    sys.exit(1)

assistant_tool_call_request_message = {
    "role": "assistant",
    "tool_calls": [
        {
            "id": response.choices[0].message.tool_calls[0].id,
            "type": response.choices[0].message.tool_calls[0].type,
            "function": response.choices[0].message.tool_calls[0].function,
        }
    ],
}

# Create a message containing the result of the function call
function_call_result_message = {
    "role": "tool",
    "content": json.dumps(
        {
            "base64_image": base64_image,
            "watermarked_base64_image": wm_base64_img,
        }
    ),
    "tool_call_id": response.choices[0].message.tool_calls[0].id,
}

# Prepare the chat completion call payload
completion_messages_payload = [
    messages[0],
    messages[1],
    assistant_tool_call_request_message,
    function_call_result_message,
]

# Call the OpenAI API's chat completions endpoint to send the tool call result back to the model
# LM Studio
try:
    response = client.chat.completions.create(
        model=model,
        messages=completion_messages_payload,
    )
except Exception as e:
    print(f"Error: Failed to get final response from LM Studio API: {e}", file=sys.stderr)
    sys.exit(1)

print("\nFinal model response with knowledge of the tool call result:\n", flush=True)
if response.choices and response.choices[0].message.content:
    print(response.choices[0].message.content, flush=True)
else:
    print("Warning: No content in final response", file=sys.stderr)

