from litellm import acompletion
from pydantic import ValidationError

from ..chat.schemas import ChatHistory, ChatResponse
from ..config import LLM_API_BASE, LLM_MODEL
from ..ingestion.models import DocumentChunk
from ..llm_utils.prompts import (
    RAG,
    RefineMessageUsingHistory,
    SummarizeConversationHistory,
)
from ..utils import remove_json_markdown, setup_logger

logger = setup_logger()


async def get_llm_response(
    user_message: str, session_summary: str, similar_chunks: dict[int, DocumentChunk]
) -> RAG:
    """
    Get the response from the LLM model
    """
    context_string = get_context_string_from_search_results(similar_chunks)
    prompt = RAG.prompt.format(context=context_string, session_summary=session_summary)
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


async def get_session_summary(chat_history: ChatHistory, user_message: str) -> str:
    """
    Get the session summary from the LLM model
    """
    all_messages_dict = [
        {"AI": m.response} if isinstance(m, ChatResponse) else {"Human": m.message}
        for m in chat_history
    ]
    all_messages_str = "\n".join(
        [
            f"{k}: {v}"
            for message_dict in all_messages_dict
            for k, v in message_dict.items()
        ]
    )

    prompt = SummarizeConversationHistory.prompt.format(context=user_message)
    chat_summary = await _ask_llm_async(all_messages_str, prompt, LLM_MODEL)

    logger.error(f"Chat history: {all_messages_str}")
    logger.error(f"Session summary: {chat_summary}")

    return chat_summary


async def get_refined_message(chat_summary: str, user_message: str) -> str:
    """
    Given chat summary, refine the user message to add context and make it less
    ambiguous.
    """
    prompt = RefineMessageUsingHistory.prompt.format(context=chat_summary)
    refined_message = await _ask_llm_async(user_message, prompt, LLM_MODEL)
    logger.error(f"User message: {user_message}")
    logger.error(f"Refined message: {refined_message}")

    return refined_message


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
        # "response_format": {"type": "json_object"},
    }

    if model.startswith("ollama"):
        params["api_base"] = LLM_API_BASE

    llm_response_raw = await acompletion(**params)
    logger.info(f"LLM output: {llm_response_raw.choices[0].message.content}")
    return llm_response_raw.choices[0].message.content
