import json
from tqdm import tqdm
from huggingface_hub import InferenceClient
import os

# Set up the Hugging Face API token
token = os.environ.get("HF_TOKEN")
if not token:
    raise ValueError("Please set HF_TOKEN environment variable")

# Initialize the client
client = InferenceClient(token=token)

# same prompt as step1_response.py; keep the <statement> placeholder
prompt = "Please respond to the following statement: <statement>\nYour response:"

# Load the statements
statement_file = json.loads(open("response/example.jsonl", "r").read())

# Use GPT-2 via the Inference API (free tier available)
model = "gpt2"

print(f"Using model: {model}")
print(f"Processing {len(statement_file)} statements...")

for i in tqdm(range(len(statement_file))):
    statement = statement_file[i]["statement"]
    full_prompt = prompt.replace("<statement>", statement)

    try:
        # Generate response using HF Inference API
        response = client.text_generation(
            full_prompt,
            model=model,
            max_new_tokens=100,
            return_full_text=False
        )
        statement_file[i]["response"] = response.strip()
    except Exception as e:
        print(f"\nError on statement {i}: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        statement_file[i]["response"] = ""
        if i == 0:  # Only show detailed error for first one
            break

# Save in jsonl style with indent 4
output_file = "response/" + model.split('/')[-1] + ".jsonl"
with open(output_file, "w") as f:
    json.dump(statement_file, f, indent=4)

print(f"\nSaved to {output_file}")
