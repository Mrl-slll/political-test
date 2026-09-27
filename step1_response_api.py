import json
import argparse
from tqdm import tqdm

# same prompt as step1_response.py; keep the <statement> placeholder
prompt = "Please respond to the following statement: <statement>\nYour response:"

def make_generator(provider, model):
    if provider == "openai":
        from openai import OpenAI
        client = OpenAI()  # reads OPENAI_API_KEY

        def generate(text):
            result = client.chat.completions.create(
                model = model,
                messages = [{"role": "user", "content": text}],
            )
            return result.choices[0].message.content or ""
        return generate

    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

        def generate(text):
            result = client.messages.create(
                model = model,
                max_tokens = 1024,
                messages = [{"role": "user", "content": text}],
            )
            if result.stop_reason == "refusal":
                return ""
            return "".join(block.text for block in result.content if block.type == "text")
        return generate

    raise ValueError("unknown provider: " + provider)

if __name__ == "__main__":

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-p", "--provider", choices = ["openai", "anthropic"], help="API provider")
    argParser.add_argument("-m", "--model", help="model name, e.g. gpt-5 or claude-opus-5")
    argParser.add_argument("-r", "--runs", default = 1, type = int, help="number of independent runs (the paper averaged 5)")
    argParser.add_argument("-l", "--limit", default = None, type = int, help="only answer the first N statements (for smoke tests)")

    args = argParser.parse_args()
    generate = make_generator(args.provider, args.model)
    name = args.model[args.model.find('/') + 1:]

    for run in range(1, args.runs + 1):
        statement_file = json.loads(open("response/example.jsonl", "r").read())
        if args.limit:
            statement_file = statement_file[:args.limit]

        for i in tqdm(range(len(statement_file)), desc = "run " + str(run)):
            statement = statement_file[i]["statement"]
            statement_file[i]["response"] = generate(prompt.replace("<statement>", statement)).strip()

        out_name = name if args.runs == 1 else name + "_run" + str(run)
        # save in jsonl style with indent 4, same as step1_response.py
        with open("response/" + out_name + ".jsonl", "w") as f:
            json.dump(statement_file, f, indent = 4)
        print("saved response/" + out_name + ".jsonl")
