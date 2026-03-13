# Task 1 Plan – Call an LLM from Code

## LLM Provider
I will use the OpenAI-compatible API via Qwen Code.

Model:
qwen3-coder-plus

## Architecture

User question -> agent.py -> LLM API -> JSON output

Steps:
1. Parse CLI argument
2. Load environment variables from `.env.agent.secret`
3. Call OpenAI-compatible chat completion API
4. Extract response text
5. Print JSON:
{
  "answer": "...",
  "tool_calls": []
}