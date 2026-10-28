import streamlit as st
from agent_graph import agent_app

# Page configuration
st.set_page_config(
    page_title="Enterprise Data Intelligence Agent",
    page_icon="📊",
    layout="wide"
)

# Title and header
st.title("📊 Enterprise Data Intelligence Agent")
st.caption("Orchestrated via LangGraph, Model Context Protocol (MCP), and Groq LLMs")

# Sidebar - Quick query suggestions & architecture overview
with st.sidebar:
    st.header("⚙️ Agent Architecture")
    st.markdown("""
    - **Planner Node**: Translates natural language into schema-aware SQLite.
    - **Validation Node**: Executes queries, enforces read-only guardrails, and triggers self-correction loops.
    - **Synthesizer Node**: Generates C-suite executive briefings with metric citations.
    """)
    
    st.divider()
    st.header("💡 Sample Prompts")
    sample_queries = [
        "Which department had the highest revenue in Q2-2025, and what was its customer retention rate?",
        "Are there any high-risk projects currently at risk, and which department owns them?",
        "Compare the revenue and operational cost of Healthcare Solutions across Q1 and Q2."
    ]
    for sq in sample_queries:
        if st.button(sq):
            st.session_state["query_input"] = sq

# Query input
user_query = st.text_input(
    "Enter a business question:",
    value=st.session_state.get("query_input", ""),
    placeholder="e.g., Which department has the lowest customer retention rate?"
)

# Process query
if st.button("Run Analytics Agent", type="primary") and user_query:
    with st.spinner("Agent is analyzing schema, generating SQL, and validating data..."):
        initial_state = {
            "user_query": user_query,
            "generated_sql": "",
            "query_result": {},
            "validation_status": "pending",
            "error_message": "",
            "final_narrative": "",
            "retry_count": 0
        }
        
        # Invoke LangGraph
        result = agent_app.invoke(initial_state)

    # 1. Executive Summary Output
    st.subheader("📋 Executive Insight Summary")
    st.markdown(result["final_narrative"])

    st.divider()

    # 2. Transparent Audit Trail (Columns layout)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔍 Auditable SQL Query")
        st.code(result["generated_sql"], language="sql")
        
        status = result["validation_status"].upper()
        if status == "PASSED":
            st.success(f"Validation Guardrail: {status}")
        else:
            st.error(f"Validation Guardrail: {status}")
    with col2:
        st.subheader("📑 Raw Database Output")
        query_res = result.get("query_result", {})
        columns = query_res.get("columns", [])
        data = query_res.get("data", [])
        
        if columns and data:
            # Build a native Markdown table (zero dependencies, completely immune to DLL blocks)
            header = "| " + " | ".join(str(c) for c in columns) + " |"
            separator = "| " + " | ".join(["---"] * len(columns)) + " |"
            rows = ["| " + " | ".join(str(val) for val in row) + " |" for row in data]
            markdown_table = "\n".join([header, separator] + rows)
            
            st.markdown(markdown_table)
            st.caption(f"Rows returned: {len(data)}")
        else:
            st.write("No rows returned or query produced no data.")