import streamlit as st
import uuid

def init_chat_history():
    """
    Инициализировать структуру хранения истории чата в session_state.

    Функция вызывается один раз при старте приложения (или при рендере),
    чтобы гарантировать наличие ключа ``chat_history`` в session_state.
    """
    if "chat_history" not in st.session_state:
        # Храним историю как список словарей вида:
        # {"role": "user" | "assistant", "content": "текст сообщения"}
        st.session_state.chat_history = []

def reset_chat_history() -> None:
    """
    Очистить историю чата в session_state.

    Используется для реализации кнопки «Новый чат».
    Если история ещё не была инициализирована, функция просто ничего не делает.
    """
    if "chat_history" in st.session_state:
        st.session_state.chat_history = []        

def render_history() -> None:
    """
    Отрисовать всю историю чата из session_state.

    Показываем только сообщения ролей ``user`` и ``assistant``.
    Роль ``system`` здесь не используется, так как предназначена
    для внутренних промптов LLM, а не для пользовательского интерфейса.
    """
    for msg in st.session_state.chat_history:
        if msg["role"] in ("user", "assistant"):
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

def add_user_message(text: str) -> None:
    """
    Добавить в историю новое пользовательское сообщение и отрисовать его.

    :param text: Текст, введённый пользователем.
    """
    st.session_state.chat_history.append(
        {"role": "user", "content": text},
    )
    with st.chat_message("user"):
        st.write(text)

def add_assistant_message(text: str) -> None:
    """
    Добавить в историю новое сообщение ассистента и отрисовать его.

    :param text: Текст ответа модели.
    """
    st.session_state.chat_history.append(
        {"role": "assistant", "content": text},
    )
    with st.chat_message("assistant"):
        st.write(text)
def init_session_id() -> str:
    """
    Гарантировать наличие session_id в session_state и вернуть его.

    Если session_id ещё не установлен, генерируется новый случайный UUID.
    Это позволяет привязать память диалога (посредством Runnable с
    историей) к конкретной вкладке/пользовательской сессии.

    Returns:
        Строковый идентификатор текущей сессии (диалога).
    """
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

def reset_session_id() -> str:
    """
    Сгенерировать и сохранить новый session_id для нового диалога.

    Используется при нажатии кнопки «Новый чат», чтобы не только
    очистить визуальную историю, но и начать новый контекст для LLM.

    Returns:
        Новый строковый идентификатор сессии.
    """
    new_id = str(uuid.uuid4())
    st.session_state.session_id = new_id
    return new_id

