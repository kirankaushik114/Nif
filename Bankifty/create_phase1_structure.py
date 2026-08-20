from pathlib import Path

ROOT = Path(r"D:\Nif\Bankifty")

folders = [
    "ai",
    "agents",
    "docs",
    "data/ai",
]

python_files = [
    "ai/__init__.py",
    "ai/config.py",
    "ai/ollama_client.py",
    "ai/market_context.py",
    "ai/context_builder.py",
    "ai/analyzer.py",
    "agents/__init__.py",
    "agents/checkpoint.py",
    "agents/data_agent.py",
]

for folder in folders:
    folder_path = ROOT / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    print(f"FOLDER OK: {folder_path}")

for relative_file in python_files:
    file_path = ROOT / relative_file
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if file_path.exists():
        print(f"SKIP (already exists): {file_path}")
    else:
        file_path.write_text(
            f'"""Bank Nifty AI Phase 1: {file_path.name}"""\n',
            encoding="utf-8",
        )
        print(f"CREATED: {file_path}")

print()
print("Phase 1 folders and Python files created.")
print("Existing files were NOT overwritten.")