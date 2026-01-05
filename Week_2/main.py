import sys
import os
from dotenv import load_dotenv
from github_utils import fetch_readme, print_readme
from repo_summarizer import generate_summary, format_summary_for_display

load_dotenv()


def main():
    repo_name, github_token, gemini_key = parse_arguments(1)
    
    if not repo_name:
        print("Error: Repository name required")
        print("Usage: python main.py <owner/repo> [OPTIONS]")
        sys.exit(1)
    
    full_command(repo_name, github_token, gemini_key)


def parse_arguments(start_idx=2):
    if len(sys.argv) < start_idx + 1:
        return None, None, None
    
    repo_name = sys.argv[start_idx]
    github_token = None
    gemini_key = None
    
    i = start_idx + 1
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
    
    return repo_name, github_token, gemini_key


def full_command(repo_name, github_token, gemini_key):
    try:
        print(f"📚 Fetching README from {repo_name}...")
        readme_content = fetch_readme(repo_name, github_token)
        print(f"✓ README fetched successfully ({len(readme_content)} characters)")
        
        print_readme(repo_name, readme_content)
        
        print(f"🤖 Generating summary using Gemini 2.5 Flash...")
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
