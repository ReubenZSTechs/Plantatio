from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface import HuggingFacePipeline

import torch

# Sub question generator model
SUBQ_MODEL_ID = "ReubenZS/plantatio_sub_q_generation"

subq_tokenizer = AutoTokenizer.from_pretrained(SUBQ_MODEL_ID)

subq_model = AutoModelForCausalLM.from_pretrained(
    SUBQ_MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto"
)

subq_pipe = pipeline(
    "text-generation",
    model=subq_model,
    tokenizer=subq_tokenizer,
    max_new_tokens=256,
    temperature=0.3
)

subq_llm = HuggingFacePipeline(pipeline=subq_pipe)


# Answer generation model
ANSWER_MODEL_ID = "ReubenZS/plantatio_answer_generation"

answer_tokenizer = AutoTokenizer.from_pretrained(ANSWER_MODEL_ID)

answer_model = AutoModelForCausalLM.from_pretrained(
    ANSWER_MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto"
)

answer_pipe = pipeline(
    "text-generation",
    model=answer_model,
    tokenizer=answer_tokenizer,
    max_new_tokens=512,
    temperature=0.5
)

answer_llm = HuggingFacePipeline(pipeline=answer_pipe)


# Reasoning engine

REASONING_MODEL_ID = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"

reasoning_tokenizer = AutoTokenizer.from_pretrained(REASONING_MODEL_ID)

reasoning_model = AutoModelForCausalLM.from_pretrained(
    REASONING_MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto"
)

reasoning_pipe = pipeline(
    "text-generation",
    model=reasoning_model,
    tokenizer=reasoning_tokenizer,
    max_new_tokens=1024,
    temperature=0.6
)

reasoning_llm = HuggingFacePipeline(pipeline=reasoning_pipe)