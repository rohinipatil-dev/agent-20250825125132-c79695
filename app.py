import streamlit as st
from typing import List, Dict
from openai import OpenAI

# -----------------------------
# OpenAI client
# -----------------------------
@st.cache_resource
def get_client() -> OpenAI:
    return OpenAI()

# -----------------------------
# Chat logic
# -----------------------------
def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, str]] = [
            {
                "role": "assistant",
                "content": (
                    "Hi! I'm your Python programming helper. Ask me about Python syntax, "
                    "standard library, debugging, best practices, algorithms, data structures, "
                    "type hints, packaging, testing, or performance tips."
                ),
            }
        ]


def add_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})


def generate_response(client: OpenAI, model: str, temperature: float, history: List[Dict[str, str]]) -> str:
    # Prepend a system message to keep the assistant helpful and on-topic.
    system_message = {"role": "system", "content": "You are a helpful assistant."}
    try:
        response = client.chat.completions.create(
            model=model,  # "gpt-4" or "gpt-3.5-turbo"
            messages=[system_message] + history,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(str(e))


# -----------------------------
# Streamlit UI
# -----------------------------
def sidebar_controls() -> Dict[str, object]:
    st.sidebar.title("Settings")
    model = st.sidebar.selectbox(
        "Model",
        options=["gpt-4", "gpt-3.5-turbo"],
        index=0,
        help="Use gpt-4 for best quality; gpt-3.5-turbo for speed and lower cost."
    )
    temperature = st.sidebar.slider(
        "Creativity (temperature)", min_value=0.0, max_value=1.0, value=0.2, step=0.05
    )

    if st.sidebar.button("Clear chat"):
        st.session_state.messages = []

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "This chatbot focuses on Python programming. Please set your OpenAI API key via "
        "the OPENAI_API_KEY environment variable or Streamlit secrets."
    )

    return {"model": model, "temperature": temperature}


def main():
    st.set_page_config(page_title="Python Programming Chatbot", page_icon="🐍")
    st.title("🐍 Python Programming Chatbot")
    st.caption("Ask questions about Python: syntax, libraries, debugging, best practices, and more.")

    init_session_state()
    settings = sidebar_controls()
    client = get_client()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Type your Python question...")
    if user_input:
        add_message("user", user_input)
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Thinking...")

            try:
                reply = generate_response(
                    client=client,
                    model=settings["model"],
                    temperature=float(settings["temperature"]),
                    history=st.session_state.messages,
                )
            except RuntimeError as err:
                placeholder.error(f"Error: {err}")
                return

            placeholder.markdown(reply)
            add_message("assistant", reply)


if __name__ == "__main__":
    main()