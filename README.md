# GitHub Repository Agent Guide

Project Overview

Till now in building a GitHub repository analysis tool, I have done progression from basic API integration (Week 1) through advanced AI integration (Week 2).

---

##  Week 1: README Fetching

In Week 1, we built the foundational component of the project - a Python script that connects to GitHub using PyGithub to fetch and display README files from repositories. The `fetch_readme.py` script accepts repository names in the `owner/repo` format, retrieves the README.md file from the GitHub API, decodes its contents, and prints them to the terminal. The implementation includes comprehensive error handling for common scenarios such as invalid repository formats, private/inaccessible repositories, missing README files, and GitHub API errors. This module successfully demonstrates basic GitHub API integration and sets the stage for more advanced functionality.

### Week 1 Features:
- ✅ GitHub API connection using PyGithub
- ✅ Repository name validation (`owner/repo` format)
- ✅ README.md file fetching and decoding
- ✅ Content display to terminal
- ✅ Comprehensive error handling
- ✅ Support for private repositories with GitHub tokens

### Week 1 Usage:
```bash
cd Week_1
python fetch_readme.py owner/reponame
python fetch_readme.py owner/private-repo --token ghp_xxx
```

---

## 🤖 Week 2: Intelligence - AI-Powered Summarization

Building upon Week 1's foundation, Week 2 introduced artificial intelligence capabilities using Google's Gemini 2.5 Flash model. The `repo_summarizer.py` script fetches a repository's README and sends it to the Gemini API with carefully engineered prompts to generate structured, comprehensive summaries. The AI analyzes repositories and produces JSON-formatted summaries containing: an overview, key features, technologies used, use cases, getting started guide, important notes, and recommendations. The output is formatted into human-readable, emoji-enhanced displays that provide valuable insights at a glance. I have integrated the latest `google.genai` package and implemented secure API key management through `.env` files along with .gitignore.

### Week 2 Features:
- ✅ Google Gemini 2.5 Flash AI integration
- ✅ Prompt engineering for structured output
- ✅ JSON response parsing and validation
- ✅ Human-readable formatted output
- ✅ Environment variable support for API keys
- ✅ Comprehensive error handling
- ✅ Support for both public and private repositories

### Week 2 Technologies:
- **PyGithub** - GitHub API client
- **google-genai** - Latest Google AI package
- **python-dotenv** - Environment variable management
- **Gemini 2.5 Flash** - Free AI model for summarization

### Week 2 Usage:
```bash
cd Week_2
export GOOGLE_API_KEY="your_api_key"
python repo_summarizer.py Supan1410/Amazon_clone_soc
python repo_summarizer.py owner/repo --gemini-key AIzaSy...
```

### Installation:
```bash
pip install PyGithub google-genai python-dotenv
```

```bash
python main.py full Supan1410/Amazon_clone_soc
python main.py full owner/repo --github-token ghp_xxx
``` 

### Summary Output Includes:
- **Overview** - What the project does
- **Key Features** - Main functionalities
- **Technologies** - Tech stack used
- **Use Cases** - How it can be used
- **Getting Started** - Setup information
- **Important Notes** - Critical details
- **Recommendation** - Whether to explore further

---

## Getting Started

### Prerequisites:
- Python 3.8+
- PyGithub library
- Google Gemini API key (free)
- GitHub account (optional, for private repos)

### Setup:
1. Clone the repository
2. Install dependencies: `pip install PyGithub google-genai python-dotenv`
3. Get a free [Google Gemini API key](https://aistudio.google.com/apikey)
4. Create `.env` file with `GOOGLE_API_KEY=your_key`

### Quick Start:
```bash
cd Week_2
python main.py summarize owner/reponame
```

---

## 🎓 Technologies Used

| Category | Technology |
|----------|-----------|
| GitHub API | PyGithub |
| AI/LLM | Google Gemini 2.5 Flash |
| Environment | python-dotenv |
| Language | Python 3.10+ |
| API Type | REST (GitHub), gRPC (Gemini) |

```

