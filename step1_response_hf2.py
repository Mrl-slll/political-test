import json
from tqdm import tqdm
import requests
import os
import time

# Set up the Hugging Face API token
token = os.environ.get("HF_TOKEN")
if not token:
    raise ValueError("Please set HF_TOKEN environment variable")

# same prompt as step1_response.py; keep the <statement> placeholder
prompt = "Please respond to the following statement: <statement>\nYour response:"

# Load the statements
statement_file = json.loads(open("response/example.jsonl", "r").read())

# Use GPT-2 via the Inference API
model = "gpt2"
API_URL = f"https://api-inference.huggingface.co/models/{model}"
headers = {"Authorization": f"Bearer {token}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

print(f"Using model: {model}")
print(f"Processing {len(statement_file)} statements...")

for i in tqdm(range(len(statement_file))):
    statement = statement_file[i]["statement"]
    full_prompt = prompt.replace("<statement>", statement)

    try:
        # Generate response using HF Inference API
        output = query({
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 100,
                "return_full_text": False
            }
        })

        # Check if there's an error
        if isinstance(output, dict) and "error" in output:
            print(f"\nAPI Error on statement {i}: {output['error']}")
            if i == 0:  # Show first error and check if we need to wait
                print(f"Full response: {output}")
                if "loading" in output.get("error", "").lower():
                    print("Model is loading, waiting 20 seconds...")
                    time.sleep(20)
                    # Retry
                    output = query({
                        "inputs": full_prompt,
                        "parameters": {
                            "max_new_tokens": 100,
                            "return_full_text": False
                        }
                    })
            statement_file[i]["response"] = ""
        elif isinstance(output, list) and len(output) > 0:
            # Extract the generated text
            generated_text = output[0].get("generated_text", "")
            # Remove the prompt from the response if return_full_text was True
            if generated_text.startswith(full_prompt):
                generated_text = generated_text[len(full_prompt):].strip()
            statement_file[i]["response"] = generated_text
        else:
            print(f"\nUnexpected output format on statement {i}: {output}")
            statement_file[i]["response"] = ""

    except Exception as e:
        print(f"\nError on statement {i}: {type(e).__name__}: {str(e)}")
        statement_file[i]["response"] = ""

# Save in jsonl style with indent 4
output_file = "response/" + model.split('/')[-1] + ".jsonl"
with open(output_file, "w") as f:
    json.dump(statement_file, f, indent=4)

print(f"\nSaved to {output_file}")
