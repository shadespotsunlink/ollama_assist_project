import subprocess
import os
import textwrap
import difflib
import json


AUTO_MODE = False  # AI only auto-applies changes when explicitly enabled
WORKSPACE = os.path.abspath("projects")  # base folder for all projects
CURRENT_PROJECT = None  # will store project folder path
PROJECT_RESOURCE_EXTS = {
    "website": [".css", ".js", ".json"],
    "python_classroom": [".py", ".ipynb", ".csv", ".json", ".md"],
    "default": [".css", ".js", ".py", ".json", ".csv", ".md"]
}


def is_resource_file(filename, project_type="default"):
    """Determine if a file is a resource that might be a dependency."""
    exts = PROJECT_RESOURCE_EXTS.get(project_type, PROJECT_RESOURCE_EXTS["default"])
    return any(filename.endswith(ext) for ext in exts)




def get_models():
    """Return list of installed Ollama models."""
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")[1:]
    models = [line.split()[0] for line in lines if line.strip()]
    return models


def run_ollama(model, prompt):
    """Run Ollama and return full text output safely with UTF-8."""
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",       # ensures UTF-8 decoding
            errors="replace",       # replaces invalid chars instead of crashing
            shell=False
        )
        if result.returncode != 0:
            print(f"⚠️ Ollama error: {result.stderr.strip()}")
            return ""
        return result.stdout.strip()
    except Exception as e:
        print(f"⚠️ Ollama exception: {e}")
        return ""






def generate_project_plan(project_name, project_description, model):
    prompt = (
        f"You are an AI assistant helping plan a software project named '{project_name}'.\n"
        f"Project goal: {project_description}\n"
        "Return a structured JSON with a list of files. Each file should have:\n"
        "  - name\n"
        "  - description\n"
        "  - dependencies (list of filenames, optional)\n"
        "Return ONLY valid JSON — no explanations, no code fences."
    )

    plan_text = run_ollama(model, prompt).strip()

    # Strip code fences or any markdown if accidentally added
    if plan_text.startswith("```"):
        plan_text = "\n".join(plan_text.split("\n")[1:-1]).strip()

    try:
        plan = json.loads(plan_text)
        if isinstance(plan, list):
            plan = {"files": [{"name": f, "description": "", "dependencies": []} for f in plan]}
        return plan
    except json.JSONDecodeError:
        print("⚠️ Failed to parse AI response as JSON. Here's what it returned:")
        print(plan_text)
        return None



def create_project(project_name, model):
    global CURRENT_PROJECT
    project_path = os.path.join(WORKSPACE, project_name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        print(f"✅ Project folder created at '{project_path}'")
    else:
        print(f"⚠️ Project '{project_name}' already exists, using existing folder.")
    CURRENT_PROJECT = project_path

    # Get project details
    project_description = input("Enter a brief description of the project: ").strip()
    project_type = input("Enter the project type (e.g., website, python_classroom): ").strip()

    # Save context for persistent AI awareness
    context = {
        "name": project_name,
        "description": project_description,
        "type": project_type
    }
    context_file = os.path.join(project_path, "context.json")
    with open(context_file, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2)

    # Generate project plan using context
    plan = generate_project_plan(project_name, project_description, project_type, model)
    if not plan:
        print("⚠️ Failed to generate a project plan.")
        return

    # Feedback/approval loop
    while True:
        print("\n--- AI Proposed Project Plan ---")
        for file in plan.get("files", []):
            if isinstance(file, dict):
                deps = ", ".join(file.get("dependencies", []))
                name = file.get("name", "<unknown>")
                desc = file.get("description", "")
            else:
                name = file
                desc = ""
                deps = ""
            print(f"• {name}: {desc} (dependencies: {deps})")

        approve = input("\nDo you approve this plan? (y/n/f for feedback): ").strip().lower()
        if approve == "y":
            save_project_plan(project_path, plan)
            print("\n--- Generating Project Files ---")
            # Pass project_type to help dependency-aware generation
            generate_files_from_plan(plan, project_path, model, project_type=project_type)
            break
        elif approve == "f":
            feedback = input("Enter feedback to revise the plan: ").strip()
            plan = generate_project_plan(
                project_name + " (revised)",
                project_description + " | Feedback: " + feedback,
                project_type,
                model
            )
            if not plan:
                print("⚠️ Failed to generate revised plan, try again.")
        elif approve == "n":
            print("Project creation canceled.")
            return
        else:
            print("Invalid input, please enter y/n/f.")



def generate_project_plan(project_name, project_description, project_type, model):
    prompt = (
        f"You are an AI assistant helping plan a {project_type} project named '{project_name}'.\n"
        f"Project goal: {project_description}\n"
        "Please return a structured plan in JSON format with a list of files. Each file should have:\n"
        "  - name\n"
        "  - description\n"
        "  - dependencies (list of filenames, optional)\n"
        "Return ONLY valid JSON, no extra text or markdown formatting."
    )

    plan_text = run_ollama(model, prompt).strip()

    # Remove code fences if present
    if plan_text.startswith("```"):
        plan_text = "\n".join(plan_text.split("\n")[1:-1]).strip()

    try:
        plan = json.loads(plan_text)
        if isinstance(plan, list):
            plan = {"files": [{"name": f, "description": "", "dependencies": []} for f in plan]}
        return plan
    except json.JSONDecodeError:
        print("⚠️ Failed to parse AI response as JSON. Here's what it returned:")
        print(plan_text)
        return None



    
def save_project_plan(project_path, plan):
    """Save the project plan as plan.json."""
    plan_file = os.path.join(project_path, "plan.json")
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    print(f"✅ Project plan saved to {plan_file}")


def load_project_plan(project_path):
    """Load the project plan from plan.json if it exists."""
    plan_file = os.path.join(project_path, "plan.json")
    if os.path.exists(plan_file):
        with open(plan_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None
    

def generate_files_from_plan(plan, project_path, model, project_type="default"):
    files_created = set()

    # Normalize plan
    files_list = plan.get("files", []) if isinstance(plan, dict) else plan
    if not isinstance(files_list, list):
        print("⚠️ Invalid plan format")
        return

    def create_file_entry(file_entry):
        filename = os.path.join(project_path, file_entry["name"])
        deps = file_entry.get("dependencies", [])

        # Create dependencies first if they are recognized as resource files
        for dep in deps:
            dep_entry = next((f for f in files_list if f["name"] == dep), None)
            if dep_entry and dep_entry["name"] not in files_created:
                # Only create if it’s a resource for the project type
                if is_resource_file(dep_entry["name"], project_type):
                    create_file_entry(dep_entry)

        # Prepare prompt for AI
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                current_content = f.read()
            prompt = f"Here is the current content of '{file_entry['name']}':\n{current_content}\nSuggest improved content."
        else:
            current_content = None
            prompt = f"Write the initial content for '{file_entry['name']}': {file_entry.get('description','')}"

        suggestion = run_ollama(model, prompt)
        if not suggestion.strip():
            print(f"⚠️ No response for '{file_entry['name']}', skipping.")
            return

        handle_suggestion(filename, suggestion, model, original_content=current_content)
        files_created.add(file_entry["name"])

    # Loop through all files
    for f in files_list:
        if isinstance(f, dict) and f.get("name") not in files_created:
            create_file_entry(f)



def prompt_user_choice(message):
    """Ask user for Y/N approval or feedback."""
    while True:
        choice = input(f"\n{message} (y/n/f for feedback): ").strip().lower()
        if choice in ["y", "n", "f"]:
            return choice
        print("Please enter 'y', 'n', or 'f'.")


def handle_suggestion(filename, initial_suggestion, model, original_content=None):
    """Loop for approval/feedback until user applies or discards, with optional diff."""
    suggestion = initial_suggestion

    while True:
        print("\n--- AI Suggested Content Preview ---\n")

        if original_content:
            diff = difflib.unified_diff(
                original_content.splitlines(),
                suggestion.splitlines(),
                fromfile="Current",
                tofile="AI Suggestion",
                lineterm=""
            )
            diff_output = "\n".join(diff)
            if not diff_output.strip():
                print("No changes suggested by AI.")
            else:
                print(diff_output)
        else:
            print(textwrap.indent(suggestion, "  "))

        print("\n-----------------------------")

        if AUTO_MODE:
            approve = "y"
        else:
            approve = prompt_user_choice("Apply this content?")

        if approve == "y":
            with open(filename, "w", encoding="utf-8", errors="replace") as f:
                f.write(suggestion)
            print(f"✅ File '{filename}' saved.")
            break
        elif approve == "f":
            feedback = input("Enter your feedback: ")
            prompt_text = f"Revise this based on feedback '{feedback}':\n{suggestion}"
            if original_content:
                prompt_text = f"Original content:\n{original_content}\n\n{prompt_text}"
            suggestion = run_ollama(model, prompt_text)
            if not suggestion.strip():
                print("⚠️ No response from model.")
                break
        else:
            print("❌ Discarded suggestion.")
            break


def main():
    global AUTO_MODE
    print("🤖 Local AI File Assistant (powered by Ollama)\n")

    models = get_models()
    if not models:
        print("⚠️ No models found! Try running: ollama pull <model>")
        return

    model = models[0]
    print(f"✅ Default model: {model}")
    print("Commands: models  → list installed models | use <name> → switch active model | new <file> → create a new file with AI content | edit <file> → edit existing file with AI suggestions | auto on/off → toggle auto-apply mode | project new <name> → create a new project folder | quit\n")

    while True:
        user_input = input(f"({model}) > ").strip()

        if user_input in ["quit", "exit"]:
            print("👋 Goodbye!")
            break

        elif user_input == "models":
            print("\n📦 Installed models:")
            for m in models:
                print("  •", m)
            print()
            continue

        elif user_input.startswith("use "):
            _, new_model = user_input.split(" ", 1)
            if new_model in models:
                model = new_model
                print(f"✅ Switched to model: {model}")
            else:
                print(f"⚠️ Model '{new_model}' not found.")
            continue

        elif user_input.startswith("auto "):
            _, mode = user_input.split(" ", 1)
            if mode.lower() == "on":
                AUTO_MODE = True
                print("⚙️ Auto mode enabled — AI can apply changes without asking.")
            elif mode.lower() == "off":
                AUTO_MODE = False
                print("⚙️ Auto mode disabled — approval required.")
            else:
                print("Usage: auto on/off")
            continue

        elif user_input.startswith("new "):
            _, filename = user_input.split(" ", 1)
            topic = input("What should the file be about? ")
            prompt = f"Write a complete draft for a file about: {topic}"
            suggestion = run_ollama(model, prompt)
            if not suggestion.strip():
                print("⚠️ No response from model.")
                continue

            handle_suggestion(filename, suggestion, model)

        elif user_input.startswith("edit "):
            _, filename = user_input.split(" ", 1)
            if not os.path.exists(filename):
                print(f"⚠️ File '{filename}' not found.")
                continue

            with open(filename, "r", encoding="utf-8", errors="replace") as f:
                current_content = f.read()

            prompt = (
                f"You are an editor. Here is the current content of '{filename}':\n"
                f"{current_content}\n\n"
                "Suggest improved or reworked content while keeping the same general purpose."
            )

            suggestion = run_ollama(model, prompt)
            if not suggestion.strip():
                print("⚠️ No response from model.")
                continue

            handle_suggestion(filename, suggestion, model, original_content=current_content)
            
        elif user_input.startswith("project new "):
            _, _, project_name = user_input.split(" ", 2)
            create_project(project_name, model)



        else:
            response = run_ollama(model, user_input)
            print("\n💬", response, "\n")


if __name__ == "__main__":
    main()
