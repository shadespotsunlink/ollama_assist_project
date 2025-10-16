# Ollama Assistant

A Python-based AI assistant that leverages Ollama for local AI-powered file and project management. This tool provides an interactive command-line interface for creating, editing, and managing files and projects with AI assistance.

## Features

### 🤖 AI-Powered File Management
- **Create new files** with AI-generated content based on your descriptions
- **Edit existing files** with AI suggestions and improvements
- **Interactive approval system** with diff previews for changes
- **Feedback loop** for refining AI suggestions

### 📁 Project Management
- **Create structured projects** with AI-generated project plans
- **Dependency-aware file generation** based on project type
- **Project context persistence** with JSON metadata
- **Support for multiple project types** (website, python_classroom, etc.)

### ⚙️ Configuration Options
- **Auto-mode toggle** for automatic AI changes without approval
- **Model switching** between different Ollama models
- **Customizable project resource types** per project category
- **UTF-8 safe file handling** with error recovery

## Prerequisites

- **Python 3.6+**
- **Ollama** installed and running locally
- At least one Ollama model installed (e.g., `llama2`, `codellama`, `mistral`)

### Installing Ollama
1. Visit [ollama.ai](https://ollama.ai) and download Ollama for your platform
2. Install and start the Ollama service
3. Pull a model: `ollama pull llama2` (or your preferred model)

## Installation

1. Clone or download this repository
2. Ensure Python dependencies are available (all imports are from the standard library)
3. Make sure Ollama is running: `ollama list`

## Usage

### Starting the Assistant
```bash
python assistantProject.py
```

### Available Commands

#### Model Management
- `models` - List all installed Ollama models
- `use <model_name>` - Switch to a different model
- `auto on/off` - Toggle automatic AI changes (no approval required)

#### File Operations
- `new <filename>` - Create a new file with AI-generated content
- `edit <filename>` - Get AI suggestions to improve an existing file

#### Project Operations
- `project new <project_name>` - Create a new structured project
- `quit` or `exit` - Exit the assistant

#### General Chat
- Any other input is treated as a general question to the AI model

### Example Workflow

1. **Start the assistant:**
   ```bash
   python assistantProject.py
   ```

2. **Check available models:**
   ```
   (llama2) > models
   ```

3. **Create a new file:**
   ```
   (llama2) > new hello.py
   What should the file be about? A simple hello world program
   ```

4. **Create a project:**
   ```
   (llama2) > project new my_website
   Enter a brief description of the project: A personal portfolio website
   Enter the project type: website
   ```

## Project Structure

The assistant organizes projects in the `projects/` directory:

```
projects/
└── my_website/
   ├── context.json      # Project metadata
   ├── plan.json         # AI-generated project plan
   └── [generated files] # Project files
```

## Configuration

### Project Types
The assistant supports different project types with specific resource file extensions:

- **website**: `.css`, `.js`, `.json`
- **python_classroom**: `.py`, `.ipynb`, `.csv`, `.json`, `.md`
- **default**: `.css`, `.js`, `.py`, `.json`, `.csv`, `.md`

### Workspace Location
Projects are stored in the `projects/` directory by default. This can be modified by changing the `WORKSPACE` variable in the script.

## Features in Detail

### AI File Generation
- Generates complete file content based on your descriptions
- Shows diff previews when editing existing files
- Supports iterative refinement through feedback
- Handles UTF-8 encoding safely

### Project Planning
- AI creates structured project plans with file dependencies
- Interactive approval process for project plans
- Context-aware file generation based on project type
- Persistent project metadata

### Error Handling
- Graceful handling of Ollama connection issues
- UTF-8 encoding with error recovery
- JSON parsing error recovery
- File system error handling

## Troubleshooting

### Common Issues

1. **"No models found" error:**
   - Ensure Ollama is running: `ollama list`
   - Install a model: `ollama pull llama2`

2. **"Ollama error" messages:**
   - Check if Ollama service is running
   - Verify model name is correct
   - Check system resources (RAM/CPU)

3. **JSON parsing errors:**
   - The AI model may return non-JSON responses
   - Try using a different model or rephrasing requests

4. **File encoding issues:**
   - The script uses UTF-8 with error recovery
   - Non-UTF-8 files will have invalid characters replaced

## Contributing

This is a simple single-file Python script. To extend functionality:

1. Add new commands in the main loop
2. Extend project types in `PROJECT_RESOURCE_EXTS`
3. Add new AI prompts for different use cases
4. Implement additional file operations

## License

This project is open source. Feel free to modify and distribute as needed.

## Dependencies

- Python standard library only
- Ollama (external service)
- No additional Python packages required

---

**Note:** This assistant requires Ollama to be running locally. All AI processing happens on your machine, ensuring privacy and offline capability.
