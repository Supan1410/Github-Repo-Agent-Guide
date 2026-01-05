from github import Github
from github.GithubException import GithubException
import sys
import os


def fetch_readme(repo_name, token=None):
    try:
        if '/' not in repo_name:
            print(f"Error: Repository name must be in format 'owner/repo', got '{repo_name}'")
            sys.exit(1)
        
        if token:
            g = Github(token)
            print("✓ Authenticated with GitHub token")
        else:
            g = Github()
            print("Note: Using unauthenticated access (limited to 60 requests/hour)")
        
        try:
            repo = g.get_user(repo_name.split('/')[0]).get_repo(repo_name.split('/')[1])
        except GithubException as e:
            print(f"Error: Repository not found or is private. Status: {e.status}")
            sys.exit(1)
        
        try:
            readme_file = repo.get_contents("README.md")
        except GithubException as e:
            if e.status == 404:
                print(f"Error: README.md not found in repository {repo_name}")
            else:
                print(f"Error: Failed to fetch README.md. Status: {e.status}")
            sys.exit(1)
        
        readme_content = readme_file.decoded_content.decode('utf-8')
        print(f"README.md from {repo_name}:\n")
        print(readme_content)
        
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__} - {str(e)}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_readme.py <owner/repo> [--token TOKEN]")
        print("       python fetch_readme.py <owner/repo> [--token-env VAR_NAME]")
        print("\nExamples:")
        print("  python fetch_readme.py torvalds/linux")
        print("  python fetch_readme.py owner/private-repo --token ghp_xxx...")
        print("  python fetch_readme.py owner/private-repo --token-env GITHUB_TOKEN")
        sys.exit(1)
    
    repo_name = sys.argv[1]
    token = None
    
    if len(sys.argv) >= 3:
        if sys.argv[2] == "--token" and len(sys.argv) >= 4:
            token = sys.argv[3]
        elif sys.argv[2] == "--token-env" and len(sys.argv) >= 4:
            env_var = sys.argv[3]
            token = os.getenv(env_var)
            if not token:
                print(f"Error: Environment variable '{env_var}' not found")
                sys.exit(1)
    
    fetch_readme(repo_name, token)


if __name__ == "__main__":
    main()


