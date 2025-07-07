# CWDoc — Chat With Documents 🚀

![License](https://img.shields.io/badge/license-NonCommercial--NoDerivatives-red)
![Made by](https://img.shields.io/badge/Made%20by-MD%20Wasiful%20Kabir-brightgreen)
![Status](https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F%20by%20Wasiful-blueviolet)

# Chat with Documents: Installation & Usage Guide

This guide provides step-by-step instructions to set up and use the "Chat with Documents" CLI tool on various operating systems.

## 1. Prerequisites

Before you begin, ensure you have the following installed on your system:

### 1.1. Python (3.10 to 3.12 recommended)

- **Windows:** Download the installer from [python.org](https://www.python.org/downloads/windows/ "null"). Make sure to check "Add Python to PATH" during installation.
- **macOS:** Python 3 is often pre-installed. If not, use Homebrew (`brew install python@3.10`) or download from [python.org](https://www.python.org/downloads/macos/ "null").
- **Linux:** Python 3 is usually pre-installed. You can install specific versions using your distribution's package manager (e.g., `sudo apt-get install python3.10` on Debian/Ubuntu).

### 1.2. Git

- **All Platforms:** Download from [git-scm.com](https://git-scm.com/downloads "null").

### 1.3. Ollama (Optional, but Recommended for Local LLMs/Embeddings)

Ollama allows you to run large language models and embedding models locally.

- **Download & Install:** Follow the instructions on the official Ollama website: [ollama.com/download](https://ollama.com/download "null")
- **Pull Models:** After installation, open your terminal/command prompt and pull the recommended models:
  - **Chat Model (e.g., Mistral):** `ollama pull mistral`
  - **Embedding Model (e.g., mxbai-embed-large):** `ollama pull mxbai-embed-large`
  - (You can pull other models as well, but these are good starting points.)
- **Verify:** Ensure Ollama is running (it usually runs in the background after installation).

### 1.4. Tesseract OCR Engine (Required for Image (PNG/JPG) Document Processing)

Tesseract is an open-source OCR (Optical Character Recognition) engine used to extract text from images.

- **Windows:**
  1. Download the installer from the official Tesseract-OCR GitHub page: [github.com/UB-Mannheim/tesseract/wiki](https://www.google.com/search?q=https://github.com/UB-Mannheim/tesseract/wiki "null") (Look for `tesseract-ocr-w64-setup-vX.XX.X.exe`).
  2. Run the installer. During installation, make sure to select "Add to PATH" or manually add the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`) to your system's PATH environment variable.
- **macOS:**
  1. Open Terminal.
  2. Install Homebrew (if you don't have it): `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
  3. Install Tesseract: `brew install tesseract`
- **Linux (Debian/Ubuntu):**
  1. Open Terminal.
  2. Update package list: `sudo apt-get update`
  3. Install Tesseract: `sudo apt-get install tesseract-ocr`
- **Linux (CentOS/RHEL/Fedora):**
  1. Open Terminal.
  2. Install Tesseract: `sudo yum install tesseract` (or `sudo dnf install tesseract` for Fedora)
- **Verify Installation:** Open a new terminal/command prompt and type `tesseract --version`. You should see version information.

## 2. Installation Steps

Follow these steps to set up the Python environment for the tool.

1. **Clone the Repository:**

   ```
   git clone <your-repository-url>
   cd Chat_with_Documents # Or whatever your project folder is named
   ```

2. **Check Python Version**
   ```
   python -V
   OR
   python3 -V
   ```
3. **Create a Virtual Environment (Recommended):** A virtual environment isolates your project's dependencies.

   ```
   python -m venv .venv
   OR
   python3 -m venv .venv
   ```

4. **Activate the Virtual Environment:**

   - **Linux/macOS:**
     ```
     source .venv/bin/activate
     ```
   - **Windows (Command Prompt):**
     ```
     .\.venv\Scripts\activate.bat
     ```
   - **Windows (PowerShell):**
     ```
     .\.venv\Scripts\Activate.ps1
     ```

   (Your terminal prompt should now show `(venv)` indicating the environment is active.)

5. **Install Python Dependencies:**

   ```
   pip install .
   ```

## 3. Initial Configuration (Setup Wizard)

The tool requires initial configuration to select your AI service, models, and data paths.

1. **Run the Setup Wizard:**

   ```
   chat-with-docs --setup
   ```

2. **Follow the Prompts:**

   - **AI Service Selection:** Choose between Ollama (local), Gemini (Google), or OpenAI.
   - **Chat Model Selection:** Select an appropriate chat model for your chosen service.
   - **Embedding Model Selection:** Select an appropriate embedding model.
     - **Important for Ollama:** If you choose Ollama and don't have dedicated embedding models installed (like `nomic-embed-text`), the tool will warn you and recommend pulling one. Using a general LLM for embeddings might result in lower search quality.
   - **Vector Store Location:** Specify where you want the vector database (`chroma` folder) to be stored. You can accept the default (`chroma` in the project root) or provide an absolute path.

3. **API Key Management (for Gemini/OpenAI):**

   - If you select Gemini or OpenAI, you will be prompted for your API key.
   - **Option 1 (Recommended - Most Secure):** Set the API key as an **environment variable** _before_ running the setup.
     - For Gemini: `GEMINI_API_KEY`
     - For OpenAI: `OPENAI_API_KEY`
     - (Refer to the "API Key Management" section below for detailed instructions on how to set environment variables persistently.)
   - **Option 2 (Less Secure):** Enter the key when prompted and choose to save it to `config.json`. This stores the key in plain text in your user's home directory (`~/.chat_with_docs/config.json`).
   - **Option 3 (Temporary):** Enter the key but choose _not_ to save it. The key will only be active for the current terminal session. You will be prompted again in future sessions.

## 4. Usage

### 4.1. Prepare Your Documents

Place your PDF, DOCX, and image (PNG, JPG, JPEG, TIFF, BMP, GIF) files into the `data/` directory within your project.

### 4.2. Populate the Document Database

This step processes your documents, creates embeddings, and stores them in the vector database.

```
chat-with-docs populate-db
```

- **To reset the database** before adding new documents (e.g., if you've changed documents or want a fresh start):
  ```
  chat-with-docs populate-db --reset
  ```
- You will see progress bars for document loading, splitting, and embedding.

### 4.3. Query Your Documents

You can query your documents in two ways:

#### 4.3.1. Interactive Mode

Enter an interactive chat session with your documents.

```
chat-with-docs query
```

- Type your questions at the `🔍 Enter your query...` prompt.
- Type `q` and press Enter to quit.
- Type `clear` and press Enter to clear the terminal screen.

#### 4.3.2. Direct Query (Single Question)

Provide your question directly as a command-line argument.

```
chat-with-docs query "What is the main topic of the report?"
```

## 5. API Key Management (Detailed)

For Gemini and OpenAI services, API keys are required. Using environment variables is the most secure method.

### 5.1. Setting Environment Variables Persistently

#### **Linux / macOS (Bash/Zsh)**

Edit your shell's profile file (e.g., `~/.bashrc`, `~/.zshrc`, or `~/.profile`) using a text editor (like `nano` or `vim`):

```
nano ~/.bashrc # or ~/.zshrc
```

Add the following lines to the end of the file, replacing `YOUR_API_KEY_HERE` with your actual key:

```
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
```

Save the file and exit the editor. Then, apply the changes:

```
source ~/.bashrc # or ~/.zshrc
```

Open a new terminal to confirm the changes are active.

#### **Windows (Command Prompt / PowerShell)**

1. **Open System Properties:** Search for "Environment Variables" in the Windows search bar and select "Edit the system environment variables."
2. **Environment Variables Dialog:** Click the "Environment Variables..." button.
3. **Create New User Variable:**

   - Under "User variables for [Your Username]", click "New...".
   - For Gemini:
     - **Variable name:** `GEMINI_API_KEY`
     - **Variable value:** `YOUR_GEMINI_API_KEY_HERE`
   - For OpenAI:
     - **Variable name:** `OPENAI_API_KEY`
     - **Variable value:** `YOUR_OPENAI_API_KEY_HERE`
   - Click OK.

4. **Apply Changes:** Click OK on all open windows. You'll need to open a **new Command Prompt or PowerShell window** for the changes to take effect.

## 6. Troubleshooting

- **"Ollama server is not running"**: Ensure Ollama is installed and running in the background. You might need to restart your computer or manually start the Ollama application.
- **"Tesseract OCR engine not found"**: Verify Tesseract is installed correctly and its executable is in your system's PATH. Refer to section 1.4.
- **"API key is missing" / "unexpected model name format"**:
  - Ensure you have configured the correct API key for your chosen service during `python main.py --setup`.
  - For Gemini, double-check that you selected `gemini-embedding-001` as the embedding model, as `text-embedding-004` can sometimes cause format issues with certain LangChain/Google API client versions.
  - Verify your API key is correctly set as an environment variable or saved in `config.json`.
- **"No documents loaded"**: Ensure your documents are in the `data/` directory and are of a supported type (PDF, DOCX, PNG, JPG, etc.).
- **"No chunks generated"**: This might happen if your documents are empty or contain only images that Tesseract cannot process.

If you encounter any other issues, please provide the full error message and your operating system details.

## License

[![License](https://img.shields.io/badge/license-NonCommercial--NoDerivatives-red)](./LICENSE)

This project is licensed under a **custom NonCommercial + No Derivatives license**.  
Usage is allowed for personal and non-commercial purposes **only**.  
For commercial use or modification, please contact:

**MD Wasiful Kabir**  
📧 wasifulkabir2023@gmail.com  
🔗 ONE STEP AHEAD OF EVERYONE 🚀
