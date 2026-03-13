# Agent

## Overview

This project implements a simple CLI agent that sends a user question
to an LLM and returns a structured JSON response.

Flow:

User -> agent.py -> LLM API -> JSON output

## LLM Provider

Provider: Qwen Code API  
Model: qwen3-coder-plus

The API uses the OpenAI-compatible chat completions interface.

## Running the agent

Example:

uv run agent.py "What does REST stand for?"


Output:


{"answer":"Representational State Transfer","tool_calls":[]}


## Environment variables

Stored in `.env.agent.secret`:

- LLM_API_KEY
- LLM_API_BASE
- LLM_MODEL