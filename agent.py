import json
import sys
import os
from pathlib import Path
import requests
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_BASE = os.getenv("LLM_API_BASE")
LLM_MODEL = os.getenv("LLM_MODEL")

LMS_API_KEY = os.getenv("LMS_API_KEY")
AGENT_API_BASE_URL = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")

client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_API_BASE)

SYSTEM_PROMPT = """
You are a system documentation agent.

Use tools to answer questions:

- read_file / list_files → for docs and source code
- query_api → for live system facts and data-dependent queries

Include source only if available.

Return answer in JSON:
{
  "answer": "...",
  "source": "optional"
}
"""

def safe_path(path: str):
    if ".." in path:
        return None
    resolved = (PROJECT_ROOT / path).resolve()
    if not str(resolved).startswith(str(PROJECT_ROOT)):
        return None
    return resolved

def read_file(path: str) -> str:
    file_path = safe_path(path)
    if not file_path or not file_path.exists():
        return "Error: file not found"
    try:
        return file_path.read_text()
    except Exception as e:
        return f"Error: {e}"

def list_files(path: str) -> str:
    dir_path = safe_path(path)
    if not dir_path or not dir_path.exists():
        return "Error: directory not found"
    try:
        return "\n".join([p.name for p in dir_path.iterdir()])
    except Exception as e:
        return f"Error: {e}"

def query_api(method: str, path: str, body: str = None) -> str:
    url = AGENT_API_BASE_URL.rstrip("/") + path
    headers = {"Authorization": f"Bearer {LMS_API_KEY}"}
    try:
        if method.upper() == "GET":
            r = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            r = requests.post(url, headers=headers, json=json.loads(body) if body else None)
        else:
            return json.dumps({"status_code": 400, "body": f"Unsupported method {method}"})
        return json.dumps({"status_code": r.status_code, "body": r.text})
    except Exception as e:
        return json.dumps({"status_code": 500, "body": str(e)})

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the repository",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_api",
            "description": "Query the deployed backend API (authenticated with LMS_API_KEY)",
            "parameters": {
                "type": "object",
                "properties": {"method": {"type": "string"}, "path": {"type": "string"}, "body": {"type": "string"}},
                "required": ["method", "path"]
            }
        }
    }
]

TOOLS_MAP = {"read_file": read_file, "list_files": list_files, "query_api": query_api}

def run_agent(question: str):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": question}]
    tool_calls_log = []
    answer = ""
    source = ""

    for _ in range(10):
        response = client.chat.completions.create(model=LLM_MODEL, messages=messages, tools=TOOLS)
        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message)
            for call in message.tool_calls:
                name = call.function.name
                args = json.loads(call.function.arguments)
                result = TOOLS_MAP.get(name, lambda **_: "Unknown tool")(**args)
                tool_calls_log.append({"tool": name, "args": args, "result": result})
                messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
            continue
        else:
            content = message.get("content") or ""
            try:
                data = json.loads(content)
                answer = data.get("answer", content)
                source = data.get("source", "")
            except:
                answer = content
                source = ""
            break

    return {"answer": answer, "source": source, "tool_calls": tool_calls_log}

def main():
    if len(sys.argv) < 2:
        print('Usage: uv run agent.py "question"')
        sys.exit(1)
    question = sys.argv[1]
    result = run_agent(question)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()