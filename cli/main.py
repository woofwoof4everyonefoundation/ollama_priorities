import argparse
import json
import os
from datetime import datetime
import requests

DATA_FILE = os.path.expanduser("~/.priorities_ollama.json")
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_priority(args):
    data = load_data()
    item = {
        "priority": args.priority,
        "title": args.title,
        "created": datetime.now().isoformat()
    }
    data.append(item)
    save_data(data)
    print(f"Added: {args.title} (priority {args.priority})")

def list_priorities(args):
    data = sorted(load_data(), key=lambda x: x["priority"])
    for i, item in enumerate(data, 1):
        print(f"{i}. [{item['priority']}] {item['title']}")

def remove_priority(args):
    data = load_data()
    index = args.index - 1
    if 0 <= index < len(data):
        removed = data.pop(index)
        save_data(data)
        print(f"Removed: {removed['title']}")
    else:
        print("Invalid index")

def summarize_priorities(args):
    data = load_data()
    if not data:
        print("No priorities to summarize.")
        return
    summary_prompt = "Summarize and categorize the following list of priorities:
"
    for item in data:
        summary_prompt += f"- [{item['priority']}] {item['title']}
"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": summary_prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        output = response.json().get("response", "").strip()
        print("Ollama Summary:")
        print(output)
    except Exception as e:
        print(f"Error contacting Ollama: {e}")

def main():
    parser = argparse.ArgumentParser(description="Manage your priorities with optional Ollama summary.")
    subparsers = parser.add_subparsers()

    add = subparsers.add_parser("add", help="Add a new priority")
    add.add_argument("priority", type=int, help="Priority level (lower is more important)")
    add.add_argument("title", type=str, help="Title of the priority item")
    add.set_defaults(func=add_priority)

    list_ = subparsers.add_parser("list", help="List all priorities")
    list_.set_defaults(func=list_priorities)

    remove = subparsers.add_parser("remove", help="Remove a priority by index")
    remove.add_argument("index", type=int, help="Index of the item to remove")
    remove.set_defaults(func=remove_priority)

    summarize = subparsers.add_parser("summarize", help="Summarize priorities using Ollama")
    summarize.set_defaults(func=summarize_priorities)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
