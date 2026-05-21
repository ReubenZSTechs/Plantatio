import time
import json
import re
import uuid
from functools import wraps
from datetime import datetime, timezone
import streamlit as st

from src.utils.CONFIG import CONFIG
from src.tools.json_parser import clean_llm_json


def log_llm_call():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            start_time = time.perf_counter()
            timestamp = datetime.now(timezone.utc).isoformat()

            try:
                response = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                response = None
                success = False
                error = str(e)

            total_latency = time.perf_counter() - start_time

            prompt = kwargs.get("prompt", None)
            if prompt is None and len(args) > 1:
                prompt = args[1]

            raw_output = None
            cleaned_debug = None

            if success and response and "message" in response:
                raw_output = response.get("message", {}).get("content")
                cleaned_debug = safe_clean_llm_output(raw_output)

                prompt_processing_time = response.get("prompt_eval_duration")
                generation_time = response.get("eval_duration")
                prompt_tokens = response.get("prompt_eval_count")
                token_count = response.get("eval_count")

                prompt_processing_time = prompt_processing_time / 1e9 if prompt_processing_time else None
                generation_time = generation_time / 1e9 if generation_time else None

                tokens_per_sec = token_count / generation_time if generation_time and generation_time > 0 else None
                time_per_token = (generation_time / token_count) * 1000 if token_count and generation_time else None

                log_entry = {
                    "request_id": request_id,
                    "timestamp": timestamp,
                    "function": func.__name__,
                    "success": success,
                    "error": error,
                    "type": "llm",

                    "total_latency": total_latency,
                    "prompt_processing_time": prompt_processing_time,
                    "generation_time": generation_time,

                    "prompt_tokens_count": prompt_tokens,
                    "tokens_generated": token_count,
                    "total_tokens": (prompt_tokens or 0) + (token_count or 0),

                    "tokens_per_sec": tokens_per_sec,
                    "time_per_token": time_per_token,

                    "temperature": kwargs.get("temperature"),

                    "prompt": prompt,

                    # 🔥 KEY ADDITIONS
                    "raw_output": safe_serialize(raw_output),
                    "cleaned_output": safe_serialize(cleaned_debug["cleaned_text"]),
                    "parsed_output": safe_serialize(cleaned_debug["parsed"]),
                    "valid_json": cleaned_debug["valid"],
                    "clean_error": cleaned_debug["error"]
                }

            else:
                log_entry = {
                    "request_id": request_id,
                    "timestamp": timestamp,
                    "function": func.__name__,
                    "success": success,
                    "error": error,
                    "type": "llm",
                    "total_latency": total_latency,
                    "prompt": prompt,
                    "raw_output": None
                }

            try:
                with open(CONFIG['LOGFILE'], "a", encoding='utf-8') as f:
                    f.write(json.dumps(log_entry) + "\n")
            except Exception:
                pass

            if not success:
                raise Exception(error)

            # # 🔥 RETURN STRUCTURED OUTPUT (CRITICAL FIX)
            # return {
            #     "raw": raw_output,
            #     "cleaned": cleaned_debug["cleaned_text"] if cleaned_debug else None,
            #     "parsed": cleaned_debug["parsed"] if cleaned_debug else None,
            #     "valid": cleaned_debug["valid"] if cleaned_debug else False
            # }

            if cleaned_debug and cleaned_debug["valid"]:
                return cleaned_debug["parsed"]

            raise Exception("Invalid JSON from LLM")

        return wrapper
    return decorator


def looks_like_json(text):
    return isinstance(text, str) and text.strip().startswith(("{", "["))


def safe_serialize(obj, max_len=1000):
    try:
        if isinstance(obj, (dict, list)):
            text = json.dumps(obj, ensure_ascii=False)
        else:
            text = str(obj)

        return text[:max_len] + "...[truncated]" if len(text) > max_len else text
    except Exception as e:
        return f"[UNSERIALIZABLE: {str(e)}]"


def safe_clean_llm_output(output: str):
    result = {
        "cleaned_text": None,
        "parsed": None,
        "valid": False,
        "error": None
    }

    try:
        if not isinstance(output, str):
            result["error"] = "Output is not string"
            return result

        # Extract JSON (object OR array)
        match = re.search(r'(\{.*\}|\[.*\])', output, re.DOTALL)
        if not match:
            result["error"] = "No JSON found"
            return result

        json_str = match.group(1)
        result["cleaned_text"] = json_str

        # Parse JSON
        parsed = json.loads(json_str)
        result["parsed"] = parsed
        result["valid"] = isinstance(parsed, (dict, list))

        if not result["valid"]:
            result["error"] = "Invalid root type"

    except Exception as e:
        result["error"] = str(e)

    return result


def log_node():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            node_id = str(uuid.uuid4())
            start_time = time.perf_counter()
            timestamp = datetime.now(timezone.utc).isoformat()

            state = args[0] if args else {}

            try:
                st.session_state["current_node"] = func.__name__
            except Exception:
                pass

            state_before_keys = list(state.keys()) if isinstance(state, dict) else []

            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)

            latency = time.perf_counter() - start_time
            result_keys = list(result.keys()) if isinstance(result, dict) else []

            log_entry = {
                "request_id": node_id,
                "timestamp": timestamp,
                "node_name": func.__name__,
                "success": success,
                "error": error,
                "latency": latency,
                "state_before_keys": state_before_keys,
                "result_keys": result_keys,
            }

            # State preview
            if isinstance(state, dict):
                log_entry["state_preview"] = {
                    k: str(type(v).__name__)
                    for k, v in state.items()
                }

            # Result preview
            if isinstance(result, dict):
                log_entry["result_preview"] = {
                    k: str(type(v).__name__)
                    for k, v in result.items()
                }

            # 🔥 Controlled LLM output inspection
            llm_logs = {}

            if isinstance(result, dict):
                for k, v in result.items():

                    # Case 1: structured LLM output (NEW format)
                    if isinstance(v, dict) and {"raw", "cleaned", "parsed"}.issubset(v.keys()):
                        llm_logs[k] = {
                            "raw": safe_serialize(v["raw"]),
                            "cleaned": safe_serialize(v["cleaned"]),
                            "parsed": safe_serialize(v["parsed"]),
                            "valid_json": v.get("valid")
                        }

                    # Case 2: raw string that looks like JSON
                    elif looks_like_json(v):
                        debug = safe_clean_llm_output(v)
                        llm_logs[k] = {
                            "raw": safe_serialize(v),
                            "cleaned": safe_serialize(debug["cleaned_text"]),
                            "parsed": safe_serialize(debug["parsed"]),
                            "valid_json": debug["valid"],
                            "error": debug["error"]
                        }

            if llm_logs:
                log_entry["llm_outputs"] = llm_logs

            log_entry["result_raw"] = safe_serialize(result)

            try:
                with open(CONFIG['NODE_LOGS'], "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")
            except Exception:
                pass

            if not success:
                raise Exception(error)

            return result

        return wrapper
    return decorator