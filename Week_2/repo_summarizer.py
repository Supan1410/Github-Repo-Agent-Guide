from github_utils import fetch_readme
import sys
import os
import json
from typing import Optional
from dotenv import load_dotenv


load_dotenv()


def fetch_readme(repo_name: str, token: Optional[str] = None) -> str:
    try:
        if '/' not in repo_name:
            raise ValueError(f"Repository name must be in format 'owner/repo', got '{repo_name}'")
        
        g = Github(token) if token else Github()
        owner, repo = repo_name.split('/', 1)
        try:
            repo_obj = g.get_user(owner).get_repo(repo)
        except GithubException as e:
            raise RuntimeError(f"Repository not found or is private. Status: {e.status}")
        
        try:
            readme_file = repo_obj.get_contents("README.md")
        except GithubException as e:
            if e.status == 404:
                raise FileNotFoundError(f"README.md not found in repository {repo_name}")
            raise RuntimeError(f"Failed to fetch README.md. Status: {e.status}")
        
        readme_content = readme_file.decoded_content.decode('utf-8')
        return readme_content
        
    except Exception as e:
        raise





def generate_summary(repo_name: str, readme_content: str, gemini_key: Optional[str] = None) -> str:
    try:
        import google.genai as genai
    except ImportError:
        raise RuntimeError("Google GenAI package not installed. Install it with: pip install google-genai")
    
    api_key = gemini_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Google API key not provided. Set GOOGLE_API_KEY environment variable or use --gemini-key.")
    
    client = genai.Client(api_key=api_key)
    prompt = f"""Analyze the following GitHub repository README and provide a structured summary.

Repository: {repo_name}
README Content:
{readme_content}

Please provide a JSON response with the following structure:
{{
    "repository_name": "{repo_name}",
    "overview": "A brief 1-2 sentence description of what the repository does",
    "key_features": ["feature1", "feature2", "feature3"],
    "technologies": ["tech1", "tech2", "tech3"],
    "use_cases": ["use case 1", "use case 2"],
    "getting_started": "Brief summary of how to get started",
    "important_notes": "Any critical information or requirements",
    "recommendation": "Is this project worth exploring? Why or why not?"
}}

Respond ONLY with the JSON object, no additional text."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        summary_text = response.text.strip()
        
        try:
            summary_json = json.loads(summary_text)
        except json.JSONDecodeError:
            start_idx = summary_text.find('{')
            end_idx = summary_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                summary_json = json.loads(summary_text[start_idx:end_idx])
            else:
                raise ValueError("Could not extract JSON from LLM response")
        
        return json.dumps(summary_json, indent=2)
        
    except Exception as e:
        raise



def format_summary_for_display(summary_json_str: str) -> str:
    try:
        summary = json.loads(summary_json_str)
    except json.JSONDecodeError:
        return summary_json_str
    
    output = []
    output.append("=" * 70)
    output.append(f"📦 Repository: {summary.get('repository_name', 'Unknown')}")
    output.append("=" * 70)
    
    output.append(f"\n📝 Overview:\n{summary.get('overview', 'N/A')}")
    
    if summary.get('key_features'):
        output.append(f"\n⭐ Key Features:")
        for feature in summary['key_features']:
            output.append(f"  • {feature}")
    
    if summary.get('technologies'):
        output.append(f"\n🛠️  Technologies:")
        for tech in summary['technologies']:
            output.append(f"  • {tech}")
    
    if summary.get('use_cases'):
        output.append(f"\n💡 Use Cases:")
        for use_case in summary['use_cases']:
            output.append(f"  • {use_case}")
    
    if summary.get('getting_started'):
        output.append(f"\n🚀 Getting Started:\n{summary['getting_started']}")
    
    if summary.get('important_notes'):
        output.append(f"\n⚠️  Important Notes:\n{summary['important_notes']}")
    
    if summary.get('recommendation'):
        output.append(f"\n✅ Recommendation:\n{summary['recommendation']}")
    
    output.append("\n" + "=" * 70)
    
    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python repo_summarizer.py <owner/repo> [OPTIONS]")
        print("\nOptions:")
        print("  --github-token TOKEN       GitHub Personal Access Token (for private repos)")
        print("  --github-token-env VAR     Environment variable containing GitHub token")
        print("  --gemini-key KEY           Google Gemini API key (or use GOOGLE_API_KEY env var)")
        print("\nExamples:")
        print("  python repo_summarizer.py torvalds/linux")
        print("  python repo_summarizer.py owner/repo --gemini-key YOUR_KEY")
        print("  GOOGLE_API_KEY=YOUR_KEY python repo_summarizer.py owner/repo")
        sys.exit(1)
    
    repo_name = sys.argv[1]
    github_token = None
    gemini_key = None
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--github-token" and i + 1 < len(sys.argv):
            github_token = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--github-token-env" and i + 1 < len(sys.argv):
            env_var = sys.argv[i + 1]
            github_token = os.getenv(env_var)
            if not github_token:
                print(f"Error: Environment variable '{env_var}' not found")
                sys.exit(1)
            i += 2
        elif sys.argv[i] == "--gemini-key" and i + 1 < len(sys.argv):
            gemini_key = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    try:
        print(f"📚 Fetching README from {repo_name}...")
        readme_content = fetch_readme(repo_name, github_token)
        print(f"✓ README fetched successfully ({len(readme_content)} characters)")
        
        print(f"\n🤖 Generating summary using Gemini 2.5 Flash...")
        summary_json = generate_summary(repo_name, readme_content, gemini_key)
        
        print("✓ Summary generated successfully\n")
        formatted_summary = format_summary_for_display(summary_json)
        print(formatted_summary)
        
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__} - {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
