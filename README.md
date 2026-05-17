# 🧪 AI Lab

A learn-by-doing playground for AI engineering. Each lesson is an interactive
mini-app that teaches one concept by making you implement it.
*VIBE CODING PROJECT*

## What's built so far

- **Prompt Playground** — A/B test two prompts side-by-side with token and latency metrics
- **Prompt Builder** — assemble prompts from the 6-component formula (Role / Task / Context / Examples / Constraints / Reasoning)

## Stack

- Python 3.13
- Streamlit (UI)
- Anthropic SDK (Claude API)

## Run locally

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# create a .env file with ANTHROPIC_API_KEY=sk-ant-...
streamlit run playground.py
```

## Roadmap

- [x] Lesson 1: Prompt engineering foundations
- [ ] Lesson 2: Structured outputs (JSON schemas)
- [ ] Lesson 3: Tool use / function calling
- [ ] Lesson 4: Mini-RAG over course notes
- [ ] Lesson 5: Agent sandbox
- [ ] Lesson 6: Eval harness