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