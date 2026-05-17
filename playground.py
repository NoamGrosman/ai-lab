import time
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()


def call_claude(prompt: str, system: str = "", max_tokens: int = 500) -> dict:
    """Send a prompt to Claude and return a dict with the response and metadata."""
    start = time.time()

    kwargs = {
        "model": "claude-sonnet-4-6",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system.strip():
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    elapsed = time.time() - start

    return {
        "text": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "stop_reason": response.stop_reason,
        "latency_seconds": round(elapsed, 2),
    }


def build_structured_prompt(task: str, context: str = "", examples: str = "", constraints: str = "", reasoning: str = "",) -> str:
    """Assemble the 5 user-side components into a single well-structured prompt.

    Role goes in the system prompt seperately. This function builds the user message using XML tags for clear section speration.
    """
    parts = []
     # Task always comes first — the model should know the goal up front
    parts.append(f"<task>\n{task.strip()}\n</task>")
    if context.strip():
        parts.append(f"<context>\n{context.strip()}\n</context>")
    if examples.strip():
        parts.append(f"<examples>\n{examples.strip()}\n</examples>")
    if constraints.strip():
        parts.append(f"<constraints>\n{constraints.strip()}\n</constraints>")
    if reasoning.strip():
        # The reasoning instruction goes LAST so it's the most recent thing 
        # in the model's "attention" before it starts generating
        parts.append(reasoning.strip())
    return "\n\n".join(parts)

# --- Page Setup ---
st.set_page_config(page_title="AI Lab", page_icon="🧪", layout="wide")
st.title("🧪 AI Lab")

# --- Tabs ---
tab_playground, tab_builder = st.tabs(["🎛️ Prompt Playground", "🏗️ Prompt Builder"])


# =====================================================
# TAB 1: Prompt Playground
# =====================================================
with tab_playground:
    st.subheader("Compare Two Prompts Side-by-Side")

    with st.expander("⚙️ Shared settings", expanded=False):
        shared_system = st.text_input("System prompt (applies to both)", placeholder="e.g., You are a concise tutor", key="pg_system",)
        shared_max_tokens = st.slider("Max tokens", min_value=50, max_value=2000, value=500, step=50, key="pg_max_tokens",)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Prompt A**")
        prompt_a = st.text_area("A", placeholder="First version", height=180, key="prompt_a", label_visibility="collapsed",)
    with col_b:
        st.markdown("**Prompt B**")
        prompt_b = st.text_area("B", placeholder="Second version", height=180, key="prompt_b", label_visibility="collapsed",)

    run_pg = st.button("⚡ Run both prompts", type="primary", use_container_width=True, key="run_playground")

    if run_pg:
        if not prompt_a.strip() or not prompt_b.strip():
            st.warning("Please enter text for both prompts before running.")
            st.stop()

        with st.spinner("Running Prompt A..."):
            try:
                result_a = call_claude(prompt_a, shared_system, shared_max_tokens)
            except Exception as e:
                st.error(f"Error running Prompt A: {e}")
                st.stop()
        with st.spinner("Running Prompt B..."):
            try:
                result_b = call_claude(prompt_b, shared_system, shared_max_tokens)
            except Exception as e:
                st.error(f"Error running Prompt B: {e}")
                st.stop()

        st.divider()
        st.subheader("📊 Results")

        res_a, res_b = st.columns(2)
        with res_a:
            st.markdown("### Prompt A Response")
            st.write(result_a["text"])
            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric("Input Tokens", result_a["input_tokens"])
            m2.metric("Output Tokens", result_a["output_tokens"])
            m3.metric("Latency (s)", result_a["latency_seconds"])

        with res_b:
            st.markdown("### Prompt B Response")
            st.write(result_b["text"])
            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric("Input Tokens", result_b["input_tokens"])
            m2.metric("Output Tokens", result_b["output_tokens"])
            m3.metric("Latency (s)", result_b["latency_seconds"])

        st.divider()
        st.subheader("🔍 Comparison")
        diff_in = result_b["input_tokens"] - result_a["input_tokens"]
        diff_out = result_b["output_tokens"] - result_a["output_tokens"]
        diff_lat = result_b["latency_seconds"] - result_a["latency_seconds"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Input token Δ (B vs A)", diff_in)
        c2.metric("Output token Δ (B vs A)", diff_out)
        c3.metric("Latency Δ (s)", diff_lat)


# =====================================================
# TAB 2: Prompt Builder
# =====================================================
with tab_builder:
    st.subheader("Build a structured prompt using the 6-component formula")
    st.caption("Role + Task + Context + Examples + Constraints + Reasoning instruction")

    # Two-column layout: form on left, preview + results on right
    form_col, preview_col = st.columns([1, 1])

    with form_col:
        st.markdown("### 1. Role (system prompt)")
        st.caption("Who should the model *be*? Sets tone, expertise, baseline behavior.")
        role = st.text_area("Role", placeholder="e.g., You are a senior ASIC verification engineer who explains concepts clearly", height=80, label_visibility="collapsed", key="pb_role",)

        st.markdown("### 2. Task")
        st.caption("What exactly should it do? One clear sentence with an action verb.")
        task = st.text_area("Task", placeholder="e.g., Explain the concept of clock gating in chip design", height=80, label_visibility="collapsed", key="pb_task",)

        st.markdown("### 3. Context")
        st.caption("Background info, inputs, who the audience is, what the model needs to know.")
        context = st.text_area("Context", placeholder="e.g., The audience is a third-year ECE student preparing for a job interview.", height=100, label_visibility="collapsed", key="pb_context",)

        st.markdown("### 4. Examples")
        st.caption("Show, don't tell. 1-3 input/output pairs work best.")
        examples = st.text_area("Examples", placeholder="e.g., \nQ: What is clock gating?\nA: Clock gating is a technique used in digital circuit design to reduce power consumption by shutting off the clock signal to portions of the circuitry when they are not in use.\n\nQ: Why is it important?\nA: It helps save power and reduce heat generation, which is crucial for battery-powered devices and high-performance chips.", height=120, label_visibility="collapsed", key="pb_examples",)

        st.markdown("### 5. Constraints")
        st.caption("Length, format, things to avoid. Be specific!")
        constraints = st.text_area("Constraints", placeholder="e.g.,\n- Exactly 3 short paragraphs\n- Use one concrete example from a real ASIC\n- Avoid jargon without defining it", height=100, label_visibility="collapsed", key="pb_constraints",)
        
        st.markdown("### 6. Reasoning instruction(optional)")
        st.caption("For complex multi-step tasks. Skip for simple prompts")
        reasoning_choice = st.selectbox("Reasoning style", options=["None", "Think step by step.", "First list you assumptionsm then work through the problem.", "Use <thinking> tags to reason before answering.", "Custom...",], label_visibility="collapsed", key="pb_reasoning_choice",)
        reasoning_custom = ""
        if reasoning_choice == "Custom...":
            reasoning_custom = st.text_input("Custom reasoning instruction", key="pb_reasoning_custom")
        reasoning = "" if reasoning_choice == "None" else (reasoning_custom if reasoning_choice == "Custom..." else reasoning_choice)

        st.markdown("---")
        builder_max_tokens = st.slider("Max tokens", min_value=50, max_value=2000, value=800, step=50, key="pb_max_tokens",)

    with preview_col:
        st.markdown("#### 📋 Preview")
        st.caption("This is what gets sent to the model.")

        # Build the assembled prompt
        assembled_user_prompt = build_structured_prompt(task=task or "[no task specified yet]", context=context, examples=examples, constraints=constraints, reasoning=reasoning,)

        with st.expander("System prompt", expanded=True):
            st.code(role if role.strip() else "(none — using model defaults)", language="text")

        with st.expander("User message", expanded=True):
            st.code(assembled_user_prompt, language="text")

        # Run button
        run_builder = st.button("🚀 Run structured prompt", type="primary", use_container_width=True, key="run_builder")

        if run_builder:
            if not task.strip():
                st.warning("At minimum, fill in the Task field.")
                st.stop()

            with st.spinner("Claude is thinking..."):
                try:
                    result = call_claude(
                        prompt=assembled_user_prompt,
                        system=role,
                        max_tokens=builder_max_tokens,
                    )
                except Exception as e:
                    st.error(f"API call failed: {e}")
                    st.stop()

            st.markdown("#### 🎯 Response")
            st.write(result["text"])

            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric("Input tokens", result["input_tokens"])
            m2.metric("Output tokens", result["output_tokens"])
            m3.metric("Latency (s)", result["latency_seconds"])

