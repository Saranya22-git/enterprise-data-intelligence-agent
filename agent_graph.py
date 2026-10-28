import os
from typing import TypedDict
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from tools import get_db_schema, execute_sql_query

load_dotenv()

# 1. Define the Graph State
class AgentState(TypedDict):
    user_query: str
    generated_sql: str
    query_result: dict
    validation_status: str
    error_message: str
    final_narrative: str
    retry_count: int

# 2. Initialize the LLM (Using your verified model)
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

# 3. Node: Generate SQL Query
def generate_sql_node(state: AgentState):
    schema = get_db_schema.invoke({})
    retry_info = ""
    if state.get("error_message"):
        retry_info = f"\nYour previous SQL query failed with this error: {state['error_message']}. Please fix it."

    prompt = f"""You are a Principal Data Analyst.
Translate this business question into a single clean SQLite SELECT query based on the database schema below.

Database Schema:
{schema}

Business Question:
"{state['user_query']}"
{retry_info}

Rules:
1. Return ONLY the raw SQL query.
2. Do NOT enclose in markdown tags like ```sql or ```.
3. Use only tables and columns present in the schema.
"""
    response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    # Strip any accidental markdown formatting
    cleaned_sql = response.replace("```sql", "").replace("```", "").strip()
    return {"generated_sql": cleaned_sql}

# 4. Node: Execute Query & Validate Data Quality
def execute_and_validate_node(state: AgentState):
    sql = state["generated_sql"]
    result = execute_sql_query.invoke({"query": sql})

    if result.get("status") == "error":
        return {
            "query_result": result,
            "validation_status": "failed",
            "error_message": result.get("message", "Unknown execution error"),
            "retry_count": state.get("retry_count", 0) + 1
        }

    return {
        "query_result": result,
        "validation_status": "passed",
        "error_message": "",
        "retry_count": state.get("retry_count", 0)
    }

# 5. Node: Synthesize Executive Business Narrative
def synthesize_insights_node(state: AgentState):
    prompt = f"""You are an Executive Data Advisor presenting to senior enterprise stakeholders.

Original Business Question:
"{state['user_query']}"

Auditable SQL Executed:
{state['generated_sql']}

Query Output Data:
Columns: {state['query_result'].get('columns')}
Rows: {state['query_result'].get('data')}

Instructions:
1. Deliver a concise, high-impact executive summary answering the question directly.
2. Quote exact numbers (e.g., revenue, percentages, variance) from the data.
3. Highlight any operational or risk implications evident in the metrics.
4. Keep the tone professional, objective, and auditable.
"""
    response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    return {"final_narrative": response}

# 6. Self-Correction Conditional Router
def validation_router(state: AgentState):
    if state["validation_status"] == "passed":
        return "synthesize"
    elif state.get("retry_count", 0) < 3:
        return "generate"  # Self-healing loop
    else:
        return "synthesize"

# 7. Assemble the StateGraph
workflow = StateGraph(AgentState)

workflow.add_node("generate", generate_sql_node)
workflow.add_node("execute_validate", execute_and_validate_node)
workflow.add_node("synthesize", synthesize_insights_node)

workflow.set_entry_point("generate")
workflow.add_edge("generate", "execute_validate")
workflow.add_conditional_edges(
    "execute_validate",
    validation_router,
    {"generate": "generate", "synthesize": "synthesize"}
)
workflow.add_edge("synthesize", END)

# Compile the agent application
agent_app = workflow.compile()