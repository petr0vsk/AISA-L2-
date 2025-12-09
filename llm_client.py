from typing import Dict

import streamlit as st
from langchain_core.chat_history import (
    InMemoryChatMessageHistory,
    BaseChatMessageHistory,
)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory


# Простое in-memory хранилище историй по session_id.
# В будущем здесь можно использовать слой доступа к БД (например, SQLite),
# сохранив тот же интерфейс get_message_history().
MEMORY_STORE: Dict[str, InMemoryChatMessageHistory] = {}


@st.cache_resource
def create_llm(api_key: str, temperature: float) -> ChatOpenAI:
    """
    Создать и закешировать экземпляр LLM-клиента.

    Args:
        api_key: API-ключ для доступа к OpenRouter.
        temperature: Температура генерации ответа.

    Returns:
        Экземпляр ChatOpenAI, готовый к использованию в цепочках LangChain.
    """
    return ChatOpenAI(
        model="deepseek/deepseek-chat",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=temperature,
        default_headers={
            # В проде сюда можно передать реальный URL вашего приложения.
            "HTTP-Referer": "YOUR_SITE_URL",
            "X-Title": "Your App Name",
        },
    )


def create_chain(system_prompt: str, llm: ChatOpenAI):
    """
    Создать prompt-цепочку с поддержкой истории сообщений.

    В prompt добавлен MessagesPlaceholder("history"), чтобы Runnable с
    памятью мог подставлять туда историю диалога.

    Args:
        system_prompt: Системный промпт, задающий стиль и поведение
            ассистента.
        llm: Экземпляр LLM-клиента.

    Returns:
        Объект Runnable (prompt | llm), ожидающий словарь с ключами
        "input" (текущий запрос пользователя) и "history"
        (список сообщений диалога).
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("history"),
            ("human", "{input}"),
        ],
    )

    return prompt | llm


def get_message_history(session_id: str) -> BaseChatMessageHistory:
    """
    Получить (или создать) объект истории чата для указанного session_id.

    Сейчас история хранится в простом словаре MEMORY_STORE в памяти
    процесса. В будущем здесь можно реализовать чтение/запись из БД
    (например, SQLite), сохранив тот же интерфейс.

    Args:
        session_id: Идентификатор диалога (сессии общения с ассистентом).

    Returns:
        Объект, реализующий интерфейс BaseChatMessageHistory, в котором
        хранятся сообщения пользователя и ассистента для данного
        session_id.
    """
    if session_id not in MEMORY_STORE:
        MEMORY_STORE[session_id] = InMemoryChatMessageHistory()
    return MEMORY_STORE[session_id]


@st.cache_resource
def create_chat_runnable(
    system_prompt: str,
    api_key: str,
    temperature: float,
) -> RunnableWithMessageHistory:
    """
    Создать Runnable с поддержкой истории сообщений (памяти диалога).

    Объединяет:
    * создание/кеширование LLM;
    * создание prompt-цепочки с history;
    * обёртку RunnableWithMessageHistory, которая:
      - по session_id достаёт/создаёт историю сообщений;
      - подставляет историю в prompt;
      - дописывает туда новые сообщения.

    Args:
        system_prompt: Текущий системный промпт.
        api_key: API-ключ OpenRouter.
        temperature: Температура генерации ответов.

    Returns:
        RunnableWithMessageHistory, готовый к вызову через .invoke(
        {"input": ...}, config={"configurable": {"session_id": ...}}).
    """
    llm = create_llm(api_key=api_key, temperature=temperature)
    chain = create_chain(system_prompt=system_prompt, llm=llm)

    # ВАЖНО: для текущей версии LangChain параметр называется
    # get_session_history, а не get_history.
    chat_runnable = RunnableWithMessageHistory(
        chain,
        get_session_history=get_message_history,
        history_messages_key="history",  # под этим ключом history попадёт в prompt
        input_messages_key="input",      # откуда брать новый ввод пользователя
    )

    return chat_runnable
