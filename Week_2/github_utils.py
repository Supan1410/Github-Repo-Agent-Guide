from github import Github
from github.GithubException import GithubException
from typing import Optional


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


def print_readme(repo_name: str, readme_content: str) -> None:
    print(f"\n{'='*70}")
    print(f"📄 README.md from {repo_name}")
    print(f"{'='*70}\n")
    print(readme_content)
    print(f"\n{'='*70}\n")
