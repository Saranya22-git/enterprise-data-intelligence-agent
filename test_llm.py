import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 1. Load your API key from .env
load_dotenv()

# 2. Connect using an active model from your list
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

# 3. Test query
response = llm.invoke("Say 'Hello Saranya, Groq setup is successful!' in one sentence.")
print("\nModel Response:", response.content)