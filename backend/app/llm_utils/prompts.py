import textwrap
from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class RAG(BaseModel):
    """Generated response based on question and retrieved context"""

    RAG_FAILURE_MESSAGE: ClassVar[str] = "FAILED"
    RAG_PROFILE_PROMPT: ClassVar[str] = textwrap.dedent(
        """
        You are a helpful question-answering AI. You understand user question and
        answer their question using the REFERENCE TEXT below. Use CONVERSATION HISTORY
        for additional context.
        """
    )

    RAG_RESPONSE_PROMPT: ClassVar[str] = RAG_PROFILE_PROMPT + textwrap.dedent(
        """
        You are going to write a JSON, whose TypeScript Interface is given below:

        interface Response {{
            extracted_info: string[];
            answer: string;
        }}


        For "extracted_info", extract from the REFERENCE TEXT below the most useful \
        information related to the core question asked by the user, and list them \
        one by one. If no useful information is found, return an empty list.
        """
        + f"""
        For "answer", understand the extracted information and user question, solve \
        the question step by step, and then provide the answer. \
        If no useful information was found in REFERENCE TEXT, respond with \
        "{RAG_FAILURE_MESSAGE}".
        """
        + """
        EXAMPLE RESPONSES:
        {{"extracted_info": ["Pineapples are a blend of pinecones and apples.", \
        "Pineapples have the shape of a pinecone."], "answer": "The 'pine-' from \
        pineapples likely come from the fact that pineapples are a hybrid of \
        pinecones and apples and its pinecone-like shape."}}
        {{"extracted_info": [], "answer": "FAILED"}}

        CONVERSATION HISTORY:
        {session_summary}

        REFERENCE TEXT:
        {context}

        IMPORTANT NOTES ON THE "answer" FIELD:
        - Answer in the language of the question.
        - Answer should be concise, to the point, and no longer than 80 words.
        - Do not include any information that is not present in the REFERENCE TEXT.
        """
    )

    model_config = ConfigDict(strict=True)

    extracted_info: list[str]
    answer: str

    prompt: ClassVar[str] = RAG_RESPONSE_PROMPT


class SummarizeConversationHistory:
    """Summarize a conversation history"""

    SUMMARY_PROFILE_PROMPT: str = textwrap.dedent(
        """
        You are an accurate conversation summarizer. \
        Summarize the previous conversation history provided under \
        CONVERSATION HISTORY in a few short sentences.
        """
    )

    SUMMARY_RESPONSE_PROMPT: str = SUMMARY_PROFILE_PROMPT + textwrap.dedent(
        """

        EXAMPLE RESPONSES:
        "User has asked about covid cases in the the district of Delhi. The system
        responded with the total number of cases in Delhi as 5000."
        """
    )

    prompt: str = SUMMARY_RESPONSE_PROMPT


class RefineMessageUsingHistory:
    REFINE_PROFILE_PROMPT: str = textwrap.dedent(
        """
        Your job is to reframe the user message to make it less ambigious by
        replacing pronounce with the actual nouns and adding any missing context
        from CONVERSATION HISTORY.

        Do not answer the user question, only paraphrase the user message.

        For example:
        "What is it's capital" -> "What is the capital of India"
        "Who is the leader of that country" -> "Who is the leader of India"
        """
    )

    REFINE_RESPONSE_PROMPT: str = REFINE_PROFILE_PROMPT + textwrap.dedent(
        """
        Only return the refined message string without any additional
        information or preamble.

        CONVERSATION HISTORY:
        {context}
        """
    )

    prompt: str = REFINE_RESPONSE_PROMPT
