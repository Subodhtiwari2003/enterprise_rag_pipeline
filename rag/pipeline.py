from rag.retriever import Retriever
from rag.generator import Generator

class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()
        self.generator = Generator()

    def run(self, query: str):
        # Step 1: Retrieve
        docs = self.retriever.get_docs(query)

        # Step 2: Format
        context = self.retriever.format_docs(docs)

        # Step 3: Generate
        response = self.generator.generate(query, context)

        return {
            "query": query,
            "context": context,
            "response": response
        }