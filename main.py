from agent_graph import agent_app

def ask_agent(question: str):
    print("=" * 70)
    print(f"USER QUERY: {question}")
    print("=" * 70)

    initial_state = {
        "user_query": question,
        "generated_sql": "",
        "query_result": {},
        "validation_status": "pending",
        "error_message": "",
        "final_narrative": "",
        "retry_count": 0
    }

    result = agent_app.invoke(initial_state)

    print("\n[AUDITABLE SQL QUERY]:")
    print(result["generated_sql"])

    print("\n[VALIDATION STATUS]:")
    print(result["validation_status"].upper())

    print("\n[RAW DATA RETRIEVED]:")
    print(result["query_result"])

    print("\n[EXECUTIVE INSIGHT SUMMARY]:")
    print(result["final_narrative"])
    print("=" * 70 + "\n")

if __name__ == "__main__":
    # Test Question 1: Cross-quarter revenue and profit analysis
    ask_agent("Which department had the highest revenue in Q2-2025, and what was its customer retention rate?")

    # Test Question 2: Risk and project delivery analysis
    ask_agent("Are there any high-risk projects currently at risk, and which department owns them?")