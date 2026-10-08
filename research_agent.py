"""
research_agent.py

This file holds the "brain" of the app:
  1. A web-search tool the agent can use (DuckDuckGo, free, no API key).
  2. ONE CrewAI agent that uses the Groq LLM.
  3. ONE task that tells the agent what report to write.
  4. A function run_research() that app.py calls.
"""

from crewai import Agent, Crew, LLM, Task
from crewai.tools import tool
from ddgs import DDGS

# Groq's OpenAI-compatible API address.
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Groq's model ID is "openai/gpt-oss-120b". The extra "openai/" in front tells CrewAI
# to use its OpenAI-compatible provider, which sends requests to GROQ_BASE_URL.
GROQ_MODEL = "openai/openai/gpt-oss-120b"


@tool
def search_web(query: str) -> str:
    """Search the web using DuckDuckGo. Input is a search query.
    Returns a numbered list of results with titles, URLs and short snippets."""
    try:
        # DDGS().text() returns a list of dictionaries, one per search result.
        results = DDGS().text(query, max_results=5)
    except Exception as error:
        # Return the error as text so the agent can recover instead of crashing.
        return f"Search failed: {error}"

    if not results:
        return "No results found for this query. Try different keywords."

    lines = []
    for number, result in enumerate(results, start=1):
        lines.append(
            f"{number}. {result.get('title', 'No title')}\n"
            f"   URL: {result.get('href', 'No URL')}\n"
            f"   Snippet: {result.get('body', 'No snippet')}"
        )
    return "\n\n".join(lines)


def run_research(topic: str, api_key: str) -> str:
    """Run the single-agent research crew and return the report as Markdown text."""

    # The LLM object tells CrewAI which model to use and how to authenticate.
    # We use CrewAI's OpenAI-compatible route instead of LiteLLM, because the LiteLLM
    # route sends an extra field ("cache_breakpoint") that Groq rejects.
    llm = LLM(
        model=GROQ_MODEL,
        base_url=GROQ_BASE_URL,  # send requests to Groq instead of OpenAI
        api_key=api_key,
        temperature=0.3,  # lower = more factual, less creative
    )

    # The one and only agent in this app.
    research_agent = Agent(
        role="Senior Research Analyst",
        goal="Find reliable, up-to-date information about a topic and write a clear, structured report.",
        backstory=(
            "You are an experienced analyst. You search the web several times with "
            "different queries, compare what you find, and only state facts that "
            "appear in your search results."
        ),
        tools=[search_web],
        llm=llm,
        verbose=True,  # prints the agent's steps in the terminal (helpful for learning)
        max_iter=8,    # safety limit on how many thinking/search steps the agent may take
    )

    # The task describes WHAT to produce. {topic} is filled in from the inputs below.
    research_task = Task(
        description=(
            "Research this topic: {topic}\n\n"
            "Use the search_web tool at least three times with different queries. "
            "Then write a report using exactly these sections:\n"
            "1. Research Title\n"
            "2. Introduction\n"
            "3. Main Findings\n"
            "4. Important Details\n"
            "5. Conclusion\n"
            "6. Sources (list the URLs you actually used from the search results)\n\n"
            "Write in clear Markdown. Do not invent URLs or facts that were not in the search results."
        ),
        expected_output="A structured Markdown research report with the six sections listed above.",
        agent=research_agent,
    )

    # A Crew groups agents and tasks together and runs them.
    crew = Crew(
        agents=[research_agent],
        tasks=[research_task],
        verbose=True,
    )

    # kickoff() starts the work. inputs fills in {topic} in the task description.
    result = crew.kickoff(inputs={"topic": topic})

    # result.raw is the plain text of the agent's final answer.
    return result.raw
