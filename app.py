import streamlit as st 
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

st.set_page_config(page_title="AI Lab", page_icon="🧪")
st.title("AI Lab - Lesson 1! 🧪")
st.caption("Your first interactive AI app")

prompt = st.text_area(
    "Your prompt",
    placeholder="Ask Claude anything...",
    height=120,
)

system_prompt = st.text_input(
    "System prompt (optional)",
    placeholder="You are a helpful assistant.",
)

max_tokens = st.slider("Max tokens", min_value=50, max_value=2000, value=500, step=50)

if st.button("Send to Claude", type="primary"):
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
        st.stop()  # halts the rest of the script for this rerun

    # Show a spinner while waiting
    with st.spinner("Claude is thinking..."):
        # Build the API call
        kwargs = {
            "model": "claude-sonnet-4-6",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt.strip():
            kwargs["system"] = system_prompt

        try:
            response = client.messages.create(**kwargs)
        except Exception as e:
            st.error(f"API call failed: {e}")
            st.stop()

        answer = response.content[0].text

    # --- Display the response ---
    st.subheader("Response")
    st.write(answer)

    # --- Display metadata ---
    st.divider()
    st.subheader("Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Input tokens", response.usage.input_tokens)
    col2.metric("Output tokens", response.usage.output_tokens)
    col3.metric("Stop reason", response.stop_reason)