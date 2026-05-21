import re
import json


def clean_llm_json(response: str):
    """
    Cleans and extracts valid JSON from LLM output.

    Strategy:
    1. Remove <think> blocks
    2. Remove markdown fences
    3. Extract first valid JSON object/array
    4. Parse safely
    """

    if not isinstance(response, str):
        raise ValueError(f"Expected string response, got {type(response)}")

    # 1. Remove <think>...</think>
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL | re.IGNORECASE)

    # 2. Remove markdown code fences
    response = re.sub(r"```(?:json)?", "", response)
    response = response.replace("```", "").strip()

    # 3. Find first JSON start
    start_idx = None
    for i, ch in enumerate(response):
        if ch in ["{", "["]:
            start_idx = i
            break

    if start_idx is None:
        raise ValueError(f"No JSON start found in response:\n{response}")

    response = response[start_idx:]

    # 4. Try direct parse first (fast path)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # 5. Fallback: bracket matching to extract valid JSON
    stack = []
    end_idx = None

    for i, ch in enumerate(response):
        if ch in ["{", "["]:
            stack.append(ch)
        elif ch in ["}", "]"]:
            if not stack:
                continue

            opening = stack.pop()

            if (opening == "{" and ch != "}") or (opening == "[" and ch != "]"):
                continue

            if not stack:
                end_idx = i + 1
                break

    if end_idx is None:
        raise ValueError(f"Could not find complete JSON structure:\n{response}")

    json_str = response[:end_idx]

    # 6. Final parse
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON after cleaning:\n{json_str}") from e