import sys
import os
from pathlib import Path
from openai import OpenAI
export LLM_API_KEY="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""

export LLM_API_BASE="https://openrouter.ai/api/v1"

export LLM_MODEL="qwen/qwen3-coder:free"

PROJECT_ROOT = Path(__file__).resolve().parent

# ENV variables
API_KEY = os.getenv("LLM_API_KEY")
API_BASE = os.getenv("LLM_API_BASE")
MODEL = os.getenv("LLM_MODEL")

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE
)

SYSTEM_PROMPT = """
You are a documentation agent.

To answer questions:

1. Use list_files to explore the wiki directory.
2. Use read_file to read documentation files.
3. Find the answer in the documentation.

Return the final answer as JSON:

{
  "answer": "...",
  "source": "wiki/file.md#section"
}

Only answer using the documentation.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    }
]


def safe_path(path: str):
    if ".." in path:
        return None

    resolved = (PROJECT_ROOT / path).resolve()

    if not str(resolved).startswith(str(PROJECT_ROOT)):
        return None

    return resolved


def read_file(path: str) -> str:
    file_path = safe_path(path)

    if not file_path:
        return "Error: invalid path"

    if not file_path.exists():
        return "Error: file not found"

    try:
        return file_path.read_text()
    except Exception as e:
        return f"Error: {e}"


def list_files(path: str) -> str:
    dir_path = safe_path(path)

    if not dir_path:
        return "Error: invalid path"

    if not dir_path.exists():
        return "Error: directory not found"

    try:
        entries = [p.name for p in dir_path.iterdir()]
        return "\n".join(entries)
    except Exception as e:
        return f"Error: {e}"


TOOLS_MAP = {
    "read_file": read_file,
    "list_files": list_files
}


def run_agent(question: str):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    tool_calls_log = []
    answer = ""
    source = ""

    for _ in range(10):

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS
        )

        message = response.choices[0].message

        # TOOL CALL
        if message.tool_calls:

            messages.append(message)

            for call in message.tool_calls:

                name = call.function.name
                args = json.loads(call.function.arguments)

                result = TOOLS_MAP.get(name, lambda **_: "Unknown tool")(**args)

                tool_calls_log.append({
                    "tool": name,
                    "args": args,
                    "result": result
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result
                })

            continue

        # FINAL ANSWER
        else:
            content = message.content

            try:
                data = json.loads(content)
                answer = data.get("answer", content)
                source = data.get("source", "")
            except:
                answer = content
                source = "unknown"

            break

    return {
        "answer": answer,
        "source": source,
        "tool_calls": tool_calls_log
    }


def main():

    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"question\"")
        sys.exit(1)

    question = sys.argv[1]

    result = run_agent(question)

        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
