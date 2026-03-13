import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv

# load env
load_dotenv(".env.agent.secret")

api_key = os.getenv("LLM_API_KEY")
api_base = os.getenv("LLM_API_BASE")
model = os.getenv("LLM_MODEL")

client = OpenAI(
    api_key=api_key,
    base_url=api_base,
)

def main():
    if len(sys.argv) < 2:
        print("No question provided", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
        )

        answer = response.choices[0].message.content.strip()

        result = {
            "answer": answer,
            "tool_calls": []
        }

        print(json.dumps(result))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()