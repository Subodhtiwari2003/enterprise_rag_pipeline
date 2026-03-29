from langchain.chat_models import ChatOpenAI
from app.config import config

class Generator:
    def __init__(self):
        # You can replace with Gemini / OSS model
        self.llm = ChatOpenAI(
            temperature=config.TEMPERATURE,
            model="gpt-3.5-turbo"
        )

    def generate(self, query: str, context: str):
        prompt = f"""
        You are an enterprise AI assistant.

        Answer the question based ONLY on the context below.
        If the answer is not in the context, say "I don't know".

        Context:
        {context}

        Question:
        {query}
        """

        response = self.llm.invoke(prompt)
        return response.content