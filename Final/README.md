# GitHub Repository Guided Tour Generator

A complete, production-ready AI-powered tool that analyzes GitHub repositories and generates comprehensive guided tours to help new developers understand codebases quickly.

## 🎯 Overview

This is a unified implementation that combines all the best features from the learning weeks:
- **Week 1**: GitHub API integration (README fetching)
- **Week 2**: LLM integration (README summarization)
- **Week 3**: Full repository analysis (guided tours)
- **Week 4**: Streamlit web interface

## ✨ Features

### Core Capabilities
- ✅ Fetches README.md from GitHub repositories
- ✅ Analyzes full repository file/folder structure
- ✅ Identifies important files automatically (docs, dependencies, config, entry points, CI/CD)
- ✅ Generates structured summaries using Google Gemini
- ✅ Generates comprehensive guided tours with step-by-step onboarding paths
- ✅ Handles large repos with depth limiting and file filtering
- ✅ Robust error handling for API limits and missing files

### Two Analysis Modes
1. **README Summary** - Quick analysis of README only (faster, less detailed)
2. **Full Guided Tour** - Complete analysis of README + repository structure (comprehensive, detailed)

### Two Interfaces
1. **CLI Interface** (`main.py`) - Command-line tool for quick analysis
2. **Web UI** (`app.py`) - Interactive Streamlit web application

## 📁 Project Structure

```
Final/
├── github_client.py    # GitHub API operations (README + repo tree fetching)
├── llm_client.py       # LLM operations (summary + guided tour generation)
├── agent.py            # Core agent orchestration
├── main.py             # CLI entry point
├── app.py              # Streamlit web application
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

### Architecture

```
┌─────────────┐
│   main.py   │  CLI Interface
│   app.py    │  Web Interface
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   agent.py   │  Orchestration Layer
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│github_client│ │ llm_client  │ │  dotenv      │
│             │ │             │ │              │
│• fetch_readme│ │• generate_  │ │• env vars   │
│• fetch_tree  │ │  summary    │ │              │
│• identify_   │ │• generate_  │ │              │
│  files       │ │  guided_tour│ │              │
│• get_stats   │ │• format_*   │ │              │
└─────────────┘ └─────────────┘ └─────────────┘
```

## 🚀 Installation

1. **Install dependencies:**
```bash
cd Final
pip install -r requirements.txt
```

2. **Set up environment variables:**
Create a `.env` file in the `Final` directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here  # Optional, for private repos or higher rate limits
```

**Get your API keys:**
- **Google Gemini API Key**: https://aistudio.google.com/app/apikey
- **GitHub Token** (optional): https://github.com/settings/tokens

## 📖 Usage

### Option 1: Command-Line Interface (CLI)

#### Basic Usage
```bash
# Full guided tour (default)
python main.py owner/repo

# README summary only
python main.py owner/repo --mode summary

# With custom options
python main.py owner/repo --max-depth 4 --gemini-key YOUR_KEY
```

#### Examples
```bash
# Analyze Streamlit repository
python main.py streamlit/streamlit

# Quick summary of Flask
python main.py pallets/flask --mode summary

# Deep analysis with custom depth
python main.py tiangolo/fastapi --max-depth 4
```

#### CLI Options
```
Usage: python main.py <owner/repo> [OPTIONS]

Options:
  --github-token TOKEN       GitHub Personal Access Token (for private repos)
  --github-token-env VAR     Environment variable containing GitHub token
  --gemini-key KEY           Google Gemini API key (or use GOOGLE_API_KEY env var)
  --max-depth N              Maximum directory depth to traverse (1-5, default: 3)
  --mode MODE                Mode: 'summary' (README only) or 'tour' (full analysis, default)
```

### Option 2: Web Interface (Streamlit)

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

**Using the UI:**
1. Enter a repository in the format `owner/repo` (e.g., `streamlit/streamlit`)
2. Choose analysis mode:
   - **Full Guided Tour**: Analyzes README + repository structure
   - **README Summary Only**: Quick README analysis
3. Adjust maximum directory depth (for Full Tour mode)
4. Click "Generate" to analyze the repository
5. View results in tabs:
   - **Guided Tour/Summary**: Formatted output
   - **Repository Stats**: Statistics and important files
   - **Raw JSON**: Complete JSON output

## 🔧 Module Details

### `github_client.py`
Handles all GitHub API operations:
- `fetch_readme()` - Fetch README.md content
- `fetch_repo_tree()` - Get repository file/folder structure
- `format_repo_tree()` - Format tree for display
- `identify_important_files()` - Categorize important files
- `get_repo_summary_stats()` - Generate repository statistics

### `llm_client.py`
Handles all LLM operations:
- `generate_summary()` - Generate README summary
- `format_summary_for_display()` - Format summary output
- `generate_guided_tour()` - Generate comprehensive guided tour
- `format_guided_tour()` - Format guided tour output

### `agent.py`
Orchestrates the complete pipeline:
- `generate_repo_summary()` - Full summary pipeline
- `generate_guided_tour_for_repo()` - Full guided tour pipeline

### `main.py`
CLI entry point with argument parsing and error handling.

### `app.py`
Streamlit web application with interactive UI.

## 📊 Output Formats

### Summary Output
- 📦 Repository name
- 📝 Overview
- ⭐ Key features
- 🛠️ Technologies
- 💡 Use cases
- 🚀 Getting started
- ⚠️ Important notes
- ✅ Recommendation

### Guided Tour Output
- 📌 One-line summary
- 📖 What the project does
- 📁 Key folders explained
- 📄 Important files to read first
- 🚀 Setup and run instructions
- 🏗️ Code organization
- 🛠️ Technologies detected
- 🧪 Testing approach
- 🚢 Deployment information
- 🎓 Step-by-step onboarding path

## 🛡️ Error Handling

The tool handles:
- Missing README files (continues with structure analysis)
- Private repositories (requires GitHub token)
- Rate limiting (with helpful error messages)
- Large repositories (depth limiting and file filtering)
- Invalid repository formats
- Missing API keys
- Network errors

## 🚢 Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Set secrets in the dashboard:
   - `GOOGLE_API_KEY`: Your Gemini API key
   - `GITHUB_TOKEN`: Your GitHub token (optional)

### Local Development

```bash
# Run Streamlit in development mode with auto-reload
streamlit run app.py --server.runOnSave true
```

## 📚 Example Repositories to Try

- `streamlit/streamlit` - Python web framework
- `pallets/flask` - Python web framework
- `tiangolo/fastapi` - Python API framework
- `django/django` - Python web framework
- `pytorch/pytorch` - Deep learning framework

## 🔍 Troubleshooting

### "Google API Key Required" Error
- Make sure `GOOGLE_API_KEY` is set in your `.env` file
- Or set it as an environment variable: `export GOOGLE_API_KEY=your_key`

### Rate Limiting
- Use a GitHub token to increase rate limits
- Wait a few minutes between requests if hitting limits

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're in the correct directory

### Large Repositories
- Reduce `--max-depth` to limit analysis scope
- The tool automatically limits tree items to 200 for LLM processing

## 🔐 Security Best Practices

- ✅ Never commit `.env` files
- ✅ Use environment variables for API keys
- ✅ Use Streamlit secrets for production deployment
- ✅ Validate all user inputs
- ✅ Handle errors gracefully without exposing sensitive info

## 🎓 Learning Path

This unified implementation demonstrates:
1. **Modular Architecture** - Clear separation of concerns
2. **API Integration** - GitHub API and LLM API usage
3. **Error Handling** - Robust error handling patterns
4. **User Interfaces** - Both CLI and web interfaces
5. **Code Organization** - Professional project structure

## 🚀 Next Steps

Consider enhancing the project with:
- Caching for frequently analyzed repos
- Export functionality (PDF, Markdown)
- More visualization options
- Comparison feature for multiple repos
- Batch processing capabilities
- Database storage for analysis history
- User authentication for web app
- API endpoint for programmatic access

## 📝 License

This project is part of a learning guide for building AI agents with GitHub integration.

## Acknowledgments

Built with:
- [PyGithub](https://pygithub.readthedocs.io/) - GitHub API wrapper
- [Google Gemini](https://ai.google.dev/) - LLM for analysis
- [Streamlit](https://streamlit.io/) - Web interface framework

