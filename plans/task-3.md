# Task 3 Plan – System Agent

## New tool: query_api

- Purpose: query the deployed backend to get live system data.
- Parameters:
  - method (string): HTTP method (GET, POST, etc.)
  - path (string): API path, e.g., /items/
  - body (string, optional): JSON request body
- Returns: JSON string with {"status_code": ..., "body": ...}
- Auth: use LMS_API_KEY from environment variables
- Base URL: AGENT_API_BASE_URL (default: http://localhost:42002)

## Agentic loop updates

- Same loop as Task 2
- Add `query_api` to tool schemas
- LLM can now choose between:
  1. read_file → for source code/docs
  2. list_files → to explore directories
  3. query_api → for live system facts / data queries
- Maximum 10 tool calls per question
- source field is optional for system questions

## System prompt strategy

- Update prompt to instruct LLM:
  - When to use query_api
  - When to use read_file/list_files
  - Include source only if available
  - Return final answer in JSON:
    ```
    {
      "answer": "...",
      "source": "...",
    }
    ```
- Emphasize calling the correct tool for the type of question

## Benchmark iteration

- Run `uv run run_eval.py`
- Note initial score and failed questions
- Iteratively fix:
  - tool implementation bugs
  - prompt instructions for LLM
  - parsing issues