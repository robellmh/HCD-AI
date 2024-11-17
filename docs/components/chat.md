You can call the `/chat` endpoint to ask questions. If a `session_id` is passed, the endpoint will retrieve conversation hhistory and use an LLM to summarize it. It will also rephrase the question and replace any pronouncs with the right nounds to remove any ambiguities.

If no `session_id` is passed, the endpoint will create a new session and return a `session_id` that can be used for future questions.

See API docs at `http://[DOMAIN]/docs` for more information on JSON request and response formats.

## Diagram

```mermaid
sequenceDiagram
    autonumber
    User->>API: POST /chat to ask question
    opt If session_id is passed
        API->>Db: Retrieve chat history if session_id is passed
        Db-->>API: Return chat hhistory
        API->>LLM: Summarize chat history
        LLM-->>API: Return summary
        API->>LLM: Rephrase question and replace pronouns
        LLM-->>API: Return rephrased questions
    end
    API->>Vector Db: Retrieve content with closest vectors to question
    Vector Db-->>API: Return closest vectors
    API->>Cross Encoder: Rerank and return top N content
    Cross Encoder-->>API: Return reranked content
    API->>LLM: Answer question using reranked content
    LLM-->>API: Return Answer
    API->>Db: Save chat history
    API-->>User: Return Answer

```
