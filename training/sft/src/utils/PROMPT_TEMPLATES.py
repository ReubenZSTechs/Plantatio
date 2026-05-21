def get_LLM_classifier_prompt(abstract):
    prompt = f"""
        You are a strict research paper classifier.

        Task:
        Analyze the abstract and determine whether the paper belongs to ANY of the following categories:

        1. Retrieval-Augmented Generation (RAG)
        2. Reinforcement Learning (RL)
        3. LangGraph / Graph-based LLM agent workflows

        Definitions:

        [RAG]
        A paper is RAG ONLY if it explicitly combines:
        - a retrieval mechanism (e.g., vector search, BM25, database lookup)
        AND
        - a generative model (e.g., LLM) that USES retrieved information during generation

        [Reinforcement Learning]
        A paper is RL if it involves:
        - agents interacting with an environment
        - learning via rewards
        - policies and value functions (e.g., MDP, Q-learning, PPO)

        [LangGraph / Graph-based LLM systems]
        A paper belongs here if it involves:
        - Orchestration of LLMs or agents
        - stateful workflows controlling execution
        - multi-step reasoning pipelines

        Important constraints:
        - Mentioning keywords alone is NOT sufficient
        - The concept must be central to the method
        - Be conservative (avoid false positives)

        Confidence rules:
        - Use a continuous score between 0.0 and 1.0
        - DO NOT use only 0 or 1
        - Use intermediate values like 0.2, 0.5, 0.8 when uncertain

        Explanation rules:
        - Explain WHY the paper was classified
        - Reference specific concepts from the abstract
        - Do NOT repeat JSON
        - Keep it concise (1–3 sentences)

        Output format (STRICT JSON):
        {{
        "is_rag": true/false,
        "is_rl": true/false,
        "is_langgraph": true/false,
        "confidence": {{
            "rag": 0.0,
            "rl": 0.0,
            "langgraph": 0.0
        }},
        "explanation": "Short justification referencing abstract concepts"
        }}

        Abstract:
        \"\"\"
        {abstract}
        \"\"\"
    """
    return prompt


def get_query_rewriter_train_prompt(query: str):
    prompt = f"""
        You are a professional academic assistant skilled at transforming complex or unclear questions into simpler, well-structured, and searchable subquestions.

        TASK:
        Break down the given query into a small set of clear and logically connected subquestions that together help answer the original query.

        INSTRUCTIONS:
        1. Each subquestion must target a distinct aspect of the original query.
        2. Subquestions must have logical dependencies where appropriate.
        3. Avoid redundancy or overlapping meaning.
        4. Avoid jargon, ambiguity, or vague pronouns (e.g., "this", "that", "it").
        5. If the query is already simple, return a list with only one refined version of the query.
        6. Give me 3 subquestions.
        7. Do not explain your reasoning.

        OUTPUT FORMAT (STRICT):
        Return ONLY a Python list of strings:
        ["subquestion_1", "subquestion_2", "subquestion_3"]

        Do NOT include explanations or additional text.

        INPUT:
        {query}
    """
    return prompt


def get_document_selector_train_prompt(question: str, list_of_documents: list[dict[str: str]]):
    prompt = f"""
        You are a helpful academic assistant skilled at selecting the most relevant documents to answer a given question.

        TASK:
        From the provided list of documents, select ONLY the documents that are necessary and sufficient to answer the question.

        INSTRUCTIONS:
        1. Select the minimum number of documents required to confidently answer the question.
        2. Avoid selecting irrelevant or redundant documents.
        3. If multiple documents contain overlapping information, prefer the most complete one.
        4. If no document is relevant, return an empty list.
        5. Do not explain your reasoning.

        OUTPUT FORMAT (STRICT):
        Return ONLY a Python list of document IDs:
        ["doc_id_1", "doc_id_2", ..., "doc_id_N"]

        Do NOT include explanations or additional text.

        INPUT QUESTION:
        {question}

        INPUT DOCUMENTS:
        {list_of_documents}
    """
    return prompt


def get_answer_generation_train_prompt(initial_query: str):
    prompt = f"""
        You are a professional academic assistant skilled at generating accurate and evidence-based answers.

        TASK:
        Using ONLY the provided documents, answer the main question.

        INSTRUCTIONS:
        1. If the documents do not contain enough information, respond with:
        "I do not know the answer".
        2. Ensure the answer is coherent, logically structured, and directly addresses the main query.
        3. Integrate the subquestions naturally into the reasoning process.
        4. Do NOT introduce external knowledge.
        5. Ensure that every claim is supported by at least one document.
        6. Do not explain your reasoning.

        OUTPUT FORMAT (STRICT):
        Provide a clear and concise paragraph as the final answer.

        INPUT QUESTION:
        {initial_query}

    """
    return prompt


def generate_question_dataset_prompt(chunk: str):
    prompt = f"""
        You are an academic assistant.

        TASK:
        Generate EXACTLY 2 high-quality questions based ONLY on the text.

        TEXT:
        {chunk}

        INSTRUCTIONS:
        1. Each question must be meaningful and non-trivial.
        2. Questions must cover DIFFERENT aspects of the text.
        3. Questions MUST be answerable using the text.
        4. DO NOT introduce external knowledge.
        5. If the text is unclear, return an empty list.

        CRITICAL OUTPUT RULES:
        - DO NOT use markdown
        - DO NOT wrap output in ```
        - Output MUST be valid JSON
        - No extra text

        OUTPUT FORMAT:
        [
            "question_1",
            "question_2"
        ]
    """
    return prompt


def generate_accepted_subquestion_dataset_prompt(question: str):
    prompt = f"""
        You are an academic assistant.

        TASK:
        Break the question into EXACTLY 3 accepted subquestions

        MAIN QUESTION:
        {question}

        STRICT RULES:
        - Subquestions MUST stay in the SAME DOMAIN as the question
        - DO NOT introduce unrelated topics (e.g., climate change, biology, etc.)
        - Use ONLY concepts present in the question
        - If the question is unclear or malformed, return []

        OUTPUT FORMAT:
        [
            "subquestion_1",
            "subquestion_2",
            "subquestion_3"
        ]

        NO markdown
        NO explanation
        """
    return prompt


def generate_rejected_subquestion_dataset_prompt(question: str):
    prompt = f"""
        You are generating rejected retrieval subquestions for RLHF training.

        MAIN QUESTION:
        {question}

        TASK:
        Generate EXACTLY 3 rejected subquestions.

        A rejected subquestion is:
        - Related to the SAME DOMAIN as the main question
        - Grammatically valid
        - Plausible for retrieval
        - But LESS useful for answering the main question

        The rejected subquestions should:
        - Be overly broad OR
        - Be partially relevant OR
        - Miss the key intent OR
        - Focus on secondary details instead of the main topic

        STRICT RULES:
        - Keep the SAME DOMAIN as the original question
        - Do NOT introduce unrelated fields or entities
        - Do NOT hallucinate fake concepts
        - Do NOT copy the original question
        - Each subquestion must be different
        - Each subquestion must be a single sentence
        - If the question is unclear, return []

        OUTPUT FORMAT:
        [
            "subquestion_1",
            "subquestion_2",
            "subquestion_3"
        ]

        NO markdown
        NO explanation
        NO extra text
    """
    return prompt


def generate_accepted_answer_dataset_prompt(question: str, documents: list[str]):
    prompt = f"""
        You are generating QA training data.

        QUESTION:
        {question}

        DOCUMENTS:
        {documents}

        TASK:
        Answer the question using ONLY the documents.

        STRICT RULES:
        - Use ONLY information from the documents
        - DO NOT explain beyond the answer
        - DO NOT summarize the full document
        - DO NOT provide lists
        - DO NOT provide bullet points
        - DO NOT provide numbered items
        - Maximum 2 sentences
        - Maximum 60 words
        - Single-line output only
        - No newline characters
        - No markdown
        - No introductory phrases
        - No concluding phrases

        If the answer is unclear, return EXACTLY:
        I do not know the answer

        OUTPUT:
        Single-line plain text only
    """
    return prompt


def generate_rejected_answer_dataset_prompt(question: str, documents: list[str]):
    prompt = f"""
        You are generating rejected answers for RLHF training.

        QUESTION:
        {question}

        DOCUMENTS:
        {documents}

        TASK:
        Generate ONE rejected answer.

        A rejected answer is:
        - Lower quality than the ideal answer
        - Still related to the documents
        - But incomplete, vague, partially incorrect, weakly relevant,
        or missing important details

        STRICT RULES:
        - Use ONLY information from the documents
        - Do NOT invent facts
        - Do NOT introduce external knowledge
        - The answer must still sound plausible
        - The answer must NOT fully answer the question
        - Prefer vague, incomplete, or weakly grounded responses
        - Maximum 2 sentences
        - Maximum 60 words
        - Single-line output only
        - No markdown
        - No bullet points
        - No numbered lists
        - No introductory phrases
        - No concluding phrases
        - No newline characters

        If the documents do not contain enough information, return EXACTLY:
        I do not know the answer

        OUTPUT:
        Single-line plain text only
    """
    return prompt