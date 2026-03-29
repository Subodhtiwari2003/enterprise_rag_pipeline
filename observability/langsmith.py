import os
from langsmith import traceable

os.environ["LANGCHAIN_API_KEY"] = "LANGCHAIN_API_KEY"
os.environ["LANGCHAIN_PROJECT"] = "enterprise-rag"

def trace(func):
    return traceable(name="enterprise_pipeline")(func)