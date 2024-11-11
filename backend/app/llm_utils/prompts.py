import textwrap
from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class RAG(BaseModel):
    """Generated response based on question and retrieved context"""

    RAG_FAILURE_MESSAGE: ClassVar[str] = "FAILED"
    RAG_PROFILE_PROMPT: ClassVar[str] = textwrap.dedent(
        """
        You are a helpful question-answering AI. You understand user question and
        answer their question using the REFERENCE TEXT below.
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
