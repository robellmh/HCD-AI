from litellm import acompletion
from pydantic import ValidationError

from ..config import LLM_API_BASE, LLM_MODEL
from ..ingestion.models import DocumentChunk
from ..llm_utils.prompts import RAG
from ..utils import remove_json_markdown, setup_logger

logger = setup_logger(__name__)


async def get_llm_response(
    user_message: str, similar_chunks: dict[int, DocumentChunk]
) -> RAG:
    """
    Get the response from the LLM model
    """
    context_string = get_context_string_from_search_results(similar_chunks)
    prompt = RAG.prompt.format(context=context_string)
    llm_answer = await _ask_llm_async(user_message, prompt, LLM_MODEL)
    llm_answer_trimmed = remove_json_markdown(llm_answer)

    try:
        response = RAG.model_validate_json(llm_answer_trimmed)
    except ValidationError as e:
        logger.error(f"Failed to parse LLM response: {e}. LLM response: {llm_answer}")
        response = RAG(extracted_info=[], answer=llm_answer_trimmed)

    return response


def get_context_string_from_search_results(
    search_results: dict[int, DocumentChunk],
) -> str:
    """
    Get the context string from the retrieved content
    """
    context_list = []
    for key, result in search_results.items():
        context_list.append(f"{key}. {result.file_name}\n{result.text}")
    context_string = "\n\n".join(context_list)
    return context_string


async def _ask_llm_async(user_message: str, system_message: str, model: str) -> str:
    """
    Ask the LLM model a question and return the response
    """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    params = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": 1024,
        "reponse_format": {"type": "json_object"},
    }

    if model.startswith("ollama"):
        params["api_base"] = LLM_API_BASE

    llm_response_raw = await acompletion(**params)
    logger.info(f"LLM output: {llm_response_raw.choices[0].message.content}")
    return llm_response_raw.choices[0].message.content
