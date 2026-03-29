from fastapi import FastAPI

app = FastAPI()

@app.post("/call_tool")
def call_tool(data: dict):
    tool = data.get("tool")
    params = data.get("params")

    if tool == "get_finance_data":
        return {"company": params["company"], "revenue": "100B"}

    elif tool == "get_hr_data":
        return {"emp_id": params["emp_id"], "role": "Data Scientist"}

    return {"error": "Unknown tool"}