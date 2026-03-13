# Task 2 Plan – Documentation Agent

## Tool schemas

The agent will expose two tools to the LLM:

### read_file
Reads a file from the repository.

Parameters:
- path (string): relative path from project root

Security:
- Reject paths containing `..`
- Resolve path relative to project root

### list_files
Lists files inside a directory.

Parameters:
- path (string): relative directory path

Security:
- Reject `..`
- Only allow paths inside the repository root

## Agentic loop

1. Send system prompt + user question + tool schemas to the LLM.
2. If the model returns tool_calls:
   - Execute each tool
   - Append result as a `tool` message
   - Repeat the loop.
3. If the model returns text:
   - Extract `answer` and `source`
   - Return JSON result.
4. Stop after 10 tool calls.

## System prompt strategy

The system prompt instructs the model to:

1. Use `list_files` to discover wiki files.
2. Use `read_file` to inspect documentation.
3. Return a final answer with a `source` reference in the form:

# Task 2 Plan – Documentation Agent

## Tool schemas

The agent will expose two tools to the LLM:

### read_file
Reads a file from the repository.

Parameters:
- path (string): relative path from project root

Security:
- Reject paths containing `..`
- Resolve path relative to project root

### list_files
Lists files inside a directory.

Parameters:
- path (string): relative directory path

Security:
- Reject `..`
- Only allow paths inside the repository root

## Agentic loop

1. Send system prompt + user question + tool schemas to the LLM.
2. If the model returns tool_calls:
   - Execute each tool
   - Append result as a `tool` message
   - Repeat the loop.
3. If the model returns text:
   - Extract `answer` and `source`
   - Return JSON result.
4. Stop after 10 tool calls.

## System prompt strategy

The system prompt instructs the model to:

1. Use `list_files` to discover wiki files.
2. Use `read_file` to inspect documentation.
3. Return a final answer with a `source` reference in the form:

wiki/file.md#section


The agent keeps track of all tool calls and returns them in the final JSON output.
