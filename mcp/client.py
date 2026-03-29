import requests

class MCPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def call(self, tool_name: str, params: dict):
        try:
            response = requests.post(
                f"{self.base_url}/call_tool",
                json={"tool": tool_name, "params": params}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}