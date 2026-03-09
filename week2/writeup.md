# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Muhammad Hasbiyan Rusyadi* \
SUNet ID: **-** \
Citations: **-**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: Analyze week2/app/services/extract.py and add a new function extract_action_items_llm(text: str) -> list[str] using the Ollama Python chat API. Use structured outputs with a JSON schema passed to the format argument. The response must be a JSON object with an action_items field containing a list of strings. Handle empty input, invalid JSON, and duplicate items. Keep the existing heuristic extractor unchanged.

```
TODO: 
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```

### Exercise 2: Add Unit Tests
Prompt: Update week2/tests/test_extract.py to add unit tests for extract_action_items_llm(). Mock the Ollama chat function with pytest monkeypatch so the tests do not depend on a real local model. Cover bullet lists, keyword-prefixed lines, empty input, duplicate items, and invalid JSON responses.
```
TODO: 

``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: Refactor the week2 FastAPI backend for TODO 3 without changing current user-facing behavior. Focus on four areas: 1) clear request/response schemas, 2) cleaner database access patterns, 3) app lifecycle/configuration using FastAPI lifespan where appropriate, and 4) consistent error handling. Keep changes small, safe, and easy to review.
```
TODO: 
``` 

Generated/Modified Code Snippets:
```
TODO: List all modified code files with the relevant line numbers. (We anticipate there may be multiple scattered changes here – just produce as comprehensive of a list as you can.)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: Update week2/app/routers/action_items.py. Add a new POST endpoint for LLM-powered extraction that uses extract_action_items_llm() from the extract service. Keep the existing heuristic extraction endpoint unchanged. Reuse or add clear request/response schemas, return JSON consistent with the existing API style, and add simple HTTPException-based error handling.

Update week2/app/routers/notes.py. Add a new GET endpoint that returns all saved notes from the database. Keep the code simple and readable, use a clear response model if the project already uses schemas, and keep error handling consistent with the rest of the FastAPI app.

Update the week2 frontend files to add two buttons: "Extract LLM" and "List Notes". Wire "Extract LLM" to the new LLM extraction endpoint using fetch() and render the returned checklist. Wire "List Notes" to the new notes endpoint using fetch() and display the saved notes clearly without breaking the current UI.
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


### Exercise 5: Generate a README from the Codebase
Prompt: 

```
TODO Generate week2/README.md from the current codebase only. Do not invent features. Document the FastAPI backend, SQLite persistence, heuristic extraction, LLM extraction with Ollama, note listing, and pytest-based tests. Use simple markdown sections and an API endpoint table.
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 