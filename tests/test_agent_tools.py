def test_merge_conflict_question():
    result = run_agent("How do you resolve a merge conflict?")

    assert "read_file" in str(result["tool_calls"])
    assert "wiki/git-workflow.md" in result["source"]

def test_list_wiki_files():
    result = run_agent("What files are in the wiki?")

    assert any(call["tool"] == "list_files" for call in result["tool_calls"])