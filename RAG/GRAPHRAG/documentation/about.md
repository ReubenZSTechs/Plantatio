<a id="top"></a>

# About the project
*This markdown file acts as a note to the architecture of the model, the pattern used, the type of models used, future works to be done, and more.*

<details>
<summary><strong>Table of Contents</strong></summary>

- [Background](#background)
- [Key Features](#key-features)
- [Langgraph Architecture](#langgraph-architecture)
- [Langgraph State](#langgraph-state)
- [LLM Models and Roles](#llm-models-and-roles)
- [Node Tasks](#node-tasks)
- [Tools](#tools)
- [Metrics Used](#metrics-used)
- [Future Work](#future-work)

</details>

---

# Background
Crawling through videos of preaches to find a specific topic or delving deeper regarding a specific topic takes a lot of time, especially if the user is not experienced or an expert in the field of theology. This application serves to act as a Q&A application, which user can ask regarding a topic in question and the application will answer the question.

<div align="right">
  <a href="#top">Back to top ⬆</a>
</div>

---

# Key Features
- **Custom-built Agent Architecture**<br>Featuring langgraph architecture for agent and state management across the entire process
- **State-of-the-art Prompting Methods**<br>Using Chain-of-Thought (CoT) prompting for consistency context and context analysis for better answer
- **Local LLM Hosting**<br>Leveraging Ollama to host local LLMs, such as Mistral, Gemma, and Llama for reasoning and working models
- **Multi LLM Model Architecture**<br>Utilizes multi LLM local models for specific tasks assigned later.


<div align="right">
  <a href="#top">Back to top ⬆</a>
</div>

---

# Langgraph Architecture
The proposed Langgraph Architecture for initial phase is as follows

```text
USER INPUT QUERY --> PROMPT REFINER --> DATA RETRIEVAL --> REASONING --> GENERATE ANSWER --> EVALUATION --> OUTPUT
```
Prompt Refiner Phase includes:
```text
REFINE PROMPT --> ANALYZE USER PROMPT CONTEXT --> GENERATE COT STEPS --> GENERATE SUB-QUESTIONS --> ANALYZE ENTITY
```

Data Retrieval Phase includes:
```text
FILTER BY ENTITY --> ADVANCED RAG DATA EXTRACTION
```

Reasoning Phase includes:
```text
                               |--> DEBATER MODEL 1 -->|
                               |                       |
REFINE DATA TO POINTS OF FACTS |--> DEBATER MODEL 2 -->|--> STORE ANSWERS --> 
                               |                       |
                               |--> DEBATER MODEL 3 -->|

CHECK CORRELATION (CONDITION)
```

Generating Answer Phase includes:
```text
GENERATION
```

Evaluation Phase includes:
```text
EVALUATE OUTPUT
```

Note: Should the metric correlation does not reach a threshold of 90%, then the reasoning phase will restart at the debater architecture; all debater models will debate again.

<div align="right">
  <a href="#top">Back to top ⬆</a>
</div>

---

# Langgraph State
The langgraph architecture will update the following state architecture as follows

<table>
    <tr>
        <td>State name</td>
        <td>Datatype</td> 
        <td>Description</td>
    </tr>
    <tr>
        <td>Initial Query</td>
        <td>str</td> 
        <td>User query input</td>
    </tr>
    <tr>
        <td>Refined Query</td>
        <td>str</td> 
        <td>Detailed and corrected version of initial query</td>
    </tr>
    <tr>
        <td>User Context</td>
        <td>str</td> 
        <td>Context of the user prompt</td>
    </tr>
    <tr>
        <td>CoT Steps</td>
        <td>List[str]</td> 
        <td>Chain of Thought steps</td>
    </tr>
    <tr>
        <td>Sub Questions</td>
        <td>List[str]</td> 
        <td>List of subquestions expanded from original query</td>
    </tr>
    <tr>
        <td>Entity Metadata</td>
        <td>List[str]</td> 
        <td>List all entity related to the original query</td>
    </tr>
    <tr>
        <td>Reasoning units</td>
        <td>List[Dict]</td> 
        <td>Units containing CoT steps, sub questions and entity</td>
    </tr>
    <tr>
        <td>Retrieved Docs</td>
        <td>List[str]</td> 
        <td>Retrieved documents from RAG</td>
    </tr>
    <tr>
        <td>Metadatas</td>
        <td>List[Dict]</td> 
        <td>Retrieved metadata documents from RAG</td>
    </tr>
    <tr>
        <td>Context</td>
        <td>str</td> 
        <td>Combined context from RAG</td>
    </tr>
    <tr>
        <td>Point of Facts</td>
        <td>List[Dict]</td> 
        <td>Fact points from context based on reasoning step</td>
    </tr>
    <tr>
        <td>Argument Debate</td>
        <td>List[str]</td> 
        <td>Contains the final arguments from respective debater models</td>
    </tr>
    <tr>
        <td>Correlation Argument</td>
        <td>float</td> 
        <td>How does each arguments correlate to one another</td>
    </tr>
    <tr>
        <td>Debate Context</td>
        <td>List[str]</td> 
        <td>Contains all arguments per round from each respective debater models</td>
    </tr>
    <tr>
        <td>Answer</td>
        <td>str</td> 
        <td>Final answer after debating</td>
    </tr>
    <tr>
        <td>Metrics</td>
        <td>Dict[str: float]</td> 
        <td>Metrics reference for evaluation</td>
    </tr>
</table>


<div align="right">
  <a href="#top">Back to top ⬆</a>
</div>

---


# Node Tasks
Each node, starting from `Understanding Phase` up to the `Evaluation Phase` will be limited to the scope of the defined tasks, but not limit to as follows.

<table>
    <tr>
        <td><b>Node</b></td>
        <td><b>Model</b></td>
        <td><b>Reason</b></td>
    </tr>
    <tr>
        <td>Prompt Refiner</td>
        <td>Worker 1</td>
        <td>Prompt will not contain any spelling errors or any grammatical errors</td>
    </tr>
    <tr>
        <td>Prompt Analyzer</td>
        <td>Worker 2</td>
        <td>User context will provide background of thinking</td>
    </tr>
    <tr>
        <td>CoT Steps Generation</td>
        <td>Worker 2</td>
        <td>Based on the user context, CoT will help guide the model's thinking</td>
    </tr>
    <tr>
        <td>Generate Sub-Questions</td>
        <td>Worker 3</td>
        <td>Guide the data retrieval RAG to extract full context data</td>
    </tr>
    <tr>
        <td>Analyze Entity</td>
        <td>Worker 4</td>
        <td>Guide the data retrieval RAG for guided-retrieval</td>
    </tr>
    <tr>
        <td>Fusion Node</td>
        <td>Worker 2</td>
        <td>Fuse between sub-questions, CoT steps and entity for retrieval query</td>
    </tr>
    <tr>
        <td>Fusion Evalutor Node</td>
        <td>Evaluator & Function</td>
        <td>Evaluate the confidence score between units of reasoning and sort based on confidence level</td>
    </tr>
    <tr>
        <td>Data Retrieval Node</td>
        <td>RAG</td>
        <td>Does entity filtering and data extraction</td>
    </tr>
    <tr>
        <td>Build context node</td>
        <td>Function</td>
        <td>Converts reasoning units into step contexts</td>
    </tr>
        <tr>
        <td>Data Point Formatter</td>
        <td>Worker 6</td>
        <td>Data points help point out facts for debater models</td>
    </tr>
    <tr>
        <td>Debating Node 1</td>
        <td>Debator 1</td>
        <td>Debate the facts and come up with argument</td>
    </tr>
    <tr>
        <td>Debating Node 2</td>
        <td>Debator 2</td>
        <td>Debate the facts and come up with argument</td>
    </tr>
    <tr>
        <td>Debating Node 3</td>
        <td>Debator 3</td>
        <td>Debate the facts and come up with argument</td>
    </tr>
        <tr>
        <td>Store answers</td>
        <td>Function</td>
        <td>Compile all arguments and store them for future reference</td>
    </tr>
        <tr>
        <td>Correlation Checker</td>
        <td>Evaluator</td>
        <td>For the following arguments, see if they correlate one another</td>
    </tr>
        <tr>
        <td>Answer Generation</td>
        <td>Worker 5</td>
        <td>Provided the user context, sub-questions, debating arguments, generate the final answer</td>
    </tr>
        <tr>
        <td>Evalution</td>
        <td>Evalutor</td>
        <td>Measure the metrics</td>
    </tr>
    </tr>
    <tr>
        <td>Print State</td>
        <td>Function</td>
        <td>Print the state in its entirerity</td>
    </tr>
</table>


<div align="right">
  <a href="#top">Back to top ⬆</a>
</div>

---

# LLM Models and Roles
In the initial phase, the proposed roles and LLM models assigned are as follows.

<table>
    <tr>
        <td><b>Role</b></td>
        <td><b>Model</b></td>
        <td><b>Parameter Count</b></td>
        <td><b>Quantized Version</b></td>
    </tr>
    <tr>
        <td>Worker 1</td>
        <td>Mistral-small3.2</td>
        <td>24B parameters</td>
        <td>4-bit</td>
    </tr>
    <tr>
        <td>Worker 2</td>
        <td>Deepseek-r1</td>
        <td>32B parameters</td>
        <td>4-bit</td>
    </tr>
    <tr>
        <td>Worker 3</td>
        <td>Gemma4</td>
        <td>31B parameters</td>
        <td>4-bit</td>
    </tr>
    <tr>
        <td>Worker 4</td>
        <td>Qwen3.5</td>
        <td>9B parameters</td>
        <td>8-bit</td>
    </tr>
    <tr>
        <td>Worker 5</td>
        <td>Qwen3.5</td>
        <td>35B parameters</td>
        <td>4-bit</td>
    </tr>
    <tr>
        <td>Worker 6</td>
        <td>Qwen3</td>
        <td>14B parameters</td>
        <td>4-bit</td>
    </tr>
    <tr>
        <td>Debator 1</td>
        <td>Deepseek-r1</td>
        <td>32B parameters</td>
        <td>4-bit</td>
    </tr>
    <tr>
        <td>Debator 2</td>
        <td>Gemma4</td>
        <td>31B parameters</td>
        <td>4-bit</td>
    </tr>
    <tr>
        <td>Debator 3</td>
        <td>Qwen3.6</td>
        <td>35B parameters</td>
        <td>4-bit</td>
    </tr>
    <tr>
        <td>Evaluator</td>
        <td>phi4-reasoning plus</td>
        <td>14B parameters</td>
        <td>4-bit</td>
    </tr>
</table>


<div align="right">
  <a href="#top">Back to top ⬆</a>
</div>

---

# Tools
*No tools are given*


<div align="right">
  <a href="#top">Back to top ⬆</a>
</div>

---

# Metrics Used
To evaluate the performance of the model, the `Evaluation` node and other functions will be defined to cover the following metrics.

<table>
    <tr>
        <td><b>Metric</b></td>
        <td><b>What does it measure?</b></td>
    </tr>
    <tr>
        <td>Latency</td>
        <td>Measure the starting time and end time of execution per node</td>
    </tr>
    <tr>
        <td>Coherence</td>
        <td>How coherant are the arguments of the models with the context and fact points</td>
    </tr>
    <tr>
        <td>Faithfulness</td>
        <td>How consistent is the summary to the actual facts</td>
    </tr>
        <tr>
        <td>Relevance</td>
        <td>Is the overall summary relevant to the key points</td>
    </tr>
    <tr>
        <td>Completeness</td>
        <td>How complete is the summary to the key points extracted</td>
    </tr>
    <tr>
        <td>Total Runtime</td>
        <td>Calculates the time it takes to reach from the starting point to the endpoint</td>
    </tr>
    <tr>
        <td>Correlation</td>
        <td>How correlate are the arguments between models</td>
    </tr>
    <tr>
        <td>Consistency</td>
        <td>How consistent is the model from the beginning to the end</td>
    </tr>
</table>


<div align="right">
  <a href="#top">Back to top ⬆</a>
</div>

---

# Future Work

- [ ] Implement a debater pattern in the `Synthesize` node and/ or the `Self-critic` node
- [ ] Implement a planning agent using the supervisor pattern at the beginning
- [ ] Implement a vector knowledge database to store all reports and generate summary report when needed
- [ ] Upgrade the system to be a chatbot thus implementing a RAG pipeline module

<div align="right">
  <a href="#top">Back to top ⬆</a>
</div>

---