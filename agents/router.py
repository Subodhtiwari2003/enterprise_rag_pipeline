class RouterAgent:
    def route(self, query: str):
        query = query.lower()

        if any(word in query for word in ["employee", "hr", "leave"]):
            return "HR"

        elif any(word in query for word in ["revenue", "finance", "profit"]):
            return "FINANCE"

        return "RAG"