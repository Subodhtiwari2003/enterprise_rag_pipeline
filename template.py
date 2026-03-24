import os

# Define project structure
structure = {
        "data": {
            "hr_docs": {},
            "finance_docs": {}
        },
        "app": {
            "main.py": "",
            "rag_chain.py": "",
            "ingestion.py": "",
            "vector_store.py": "",
            "config.py": "",
            "utils.py": ""
        },
        "langsmith.json": "",
        ".env": "",
        "requirements.txt": ""
}


def create_structure(base_path, structure_dict):
    for name, content in structure_dict.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, "w") as f:
                f.write(content)

if __name__ == "__main__":
    base_dir = os.getcwd()
    create_structure(base_dir, structure)
    print("✅ Project scaffold created successfully!")