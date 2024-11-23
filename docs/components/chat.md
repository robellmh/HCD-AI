You can call the `/chat` endpoint to ask questions. If a `chat_id` is passed, the endpoint will retrieve conversation hhistory and use an LLM to summarize it. It will also rephrase the question and replace any pronouncs with the right nounds to remove any ambiguities.

If no `chat_id` is passed, the endpoint will create a new conversation and return a `chat_id` that can be used for future questions.

See API docs at `http://[DOMAIN]/docs` for more information on JSON request and response formats.

## Diagram

```mermaid
sequenceDiagram
    autonumber
    User->>API: POST /chat to ask question
    opt If chat_id is passed
        API->>Db: Retrieve chat history if chat_id is passed
        Db-->>API: Return chat history
        API->>LLM: Summarize chat history
        LLM-->>API: Return summary
        API->>LLM: Rephrase question and replace pronouns
        LLM-->>API: Return rephrased questions
    end
    API->>API: Get embeddings for question
    API->>Vector Db: Retrieve content with closest vectors to question embeddings
    Vector Db-->>API: Return closest vectors
    API->>Cross Encoder: Rerank and return top N content
    Cross Encoder-->>API: Return reranked content
    API->>LLM: Answer question using reranked content
    LLM-->>API: Return Answer
    API->>Db: Save chat history
    API-->>User: Return Answer

```
