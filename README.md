# AI Research Agent

Enter a research topic. A single CrewAI agent searches the web with DuckDuckGo,
analyzes the results, and writes a structured report that is displayed in a Streamlit app.

**Flow:** Topic → CrewAI agent searches the web → agent analyzes results → structured report → Streamlit displays it

## Tech stack

- Python 3.10 to 3.13 (CrewAI does not support 3.14 yet)
- [CrewAI](https://docs.crewai.com/) for the agent
- [Groq](https://console.groq.com/) as the LLM provider, model `openai/gpt-oss-120b`
- [ddgs](https://pypi.org/project/ddgs/) for free DuckDuckGo web search (no search API key needed)
- [Streamlit](https://streamlit.io/) for the web interface

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
# Open .env and paste your real Groq API key after GROQ_API_KEY=
streamlit run app.py
```

Then open the local address Streamlit prints (usually http://localhost:8501).

## Deploy

Deployed on Streamlit Community Cloud. Set the main file to `app.py` and add
`GROQ_API_KEY` in the app's **Settings → Secrets** instead of uploading a `.env` file.

## Security

Never commit your real API key. `.env` and `.streamlit/secrets.toml` are listed in `.gitignore`.
