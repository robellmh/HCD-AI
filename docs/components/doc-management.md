This page details document management, including the ingestion and parsing of files, as well as searching through the files present in the Database.

### Document Ingestion
PDF files are parsed on a per-document, per-page basis. Once broken down into chunks (each of which is a page), a locally hosted model - `Alibaba-NLP/gte-base-en-v1.5` by default - generates vector embeddings for each chunk page. Each page/ chunk, with its metadata and embedding, is stored in the PostgreSQL database using vector indexing for efficient similarity search.

```mermaid
sequenceDiagram
    autonumber
    User->>API: Upload file for ingestion
    API->>DocumentService: Parse file into pages (chunks)
    DocumentService-->>API: Return page-based chunks
    API->>DocumentService: Generate embeddings for pages
    DocumentService-->>API: Return embeddings
    API->>Db: Save page chunks and embeddings
    Db-->>API: Acknowledge save
    API-->>User: Return file ID
```

#### Tip: All ingested documents can be easily viewed with their metadata by querying the `list_docs` `GET` endpoint.

### Search for similar documents

The search flow looks as follows:

```mermaid
sequenceDiagram
    autonumber
    User->>API: Enter search query for similar documents
    API->>VectorDB: Embed query and compare closest chunks to query
    VectorDB-->>API: Return closest page chunks
    opt If reranking is enabled
        API->>Cross Encoder: Rerank page chunks
        Cross Encoder-->>API: Return reranked chunks
    end
    API-->>User: Return page chunks
```

**N.B. Ingestion required administrator priveleges, whilst search will be available to all end users & administrators.**
