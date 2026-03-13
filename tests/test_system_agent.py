def test_backend_framework():
    result = run_agent("What framework does the backend use?")
    assert any(call["tool"] == "read_file" for call in result["tool_calls"])

def test_database_items_count():
    result = run_agent("How many items are in the database?")
    assert any(call["tool"] == "query_api" for call in result["tool_calls"])