from rag.pipeline import RAGPipeline
from guardrails.input_guard import validate_input
from guardrails.output_guard import validate_output
from agents.router import RouterAgent
from mcp.client import MCPClient
from observability.langsmith import trace

class EnterpriseApp:
    def __init__(self):
        self.rag = RAGPipeline()
        self.router = RouterAgent()
        self.mcp = MCPClient()

    @trace  # LangSmith tracing
    def run(self, query: str, user_role: str = "USER"):
        try:
            # 1. Input Guardrails
            query = validate_input(query)

            # 2. Routing
            route = self.router.route(query)

            # 3. Execution
            if route == "HR":
                result = self.mcp.call("get_hr_data", {"emp_id": "123"})
            elif route == "FINANCE":
                result = self.mcp.call("get_finance_data", {"company": "TCS"})
            else:
                result = self.rag.run(query)["response"]

            # 4. Output Guardrails
            result = validate_output(str(result))

            return result

        except Exception as e:
            return f"Error: {str(e)}"


def main():
    app = EnterpriseApp()

    while True:
        query = input("\nEnter query (or 'exit'): ")

        if query.lower() == "exit":
            break

        response = app.run(query)

        print("\n--- RESPONSE ---")
        print(response)


if __name__ == "__main__":
    main()