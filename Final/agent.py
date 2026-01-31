"""
Core Agent
Orchestrates GitHub data fetching and LLM processing to generate summaries and guided tours.
"""

from typing import Optional, Dict, List
from dotenv import load_dotenv
from github_client import (
    fetch_readme,
    fetch_repo_tree,
    identify_important_files,
    get_repo_summary_stats
)
from llm_client import (
    generate_summary,
    format_summary_for_display,
    generate_guided_tour,
    format_guided_tour
)

load_dotenv()


def generate_repo_summary(
    repo_name: str,
    github_token: Optional[str] = None,
    gemini_key: Optional[str] = None
) -> Dict[str, any]:
    """
    Generate a summary of a repository from its README.
    
    Args:
        repo_name: Repository in format 'owner/repo'
        github_token: Optional GitHub token
        gemini_key: Optional Gemini API key
        
    Returns:
        Dictionary with 'summary_json' and 'formatted_summary' keys
    """
    # Fetch README
    readme_content = ""
    try:
        readme_content = fetch_readme(repo_name, github_token)
    except FileNotFoundError:
        readme_content = "README.md not found in repository."
    except Exception as e:
        readme_content = f"Error fetching README: {str(e)}"
    
    # Generate summary
    summary_json = generate_summary(repo_name, readme_content, gemini_key)
    
    # Format for display
    formatted_summary = format_summary_for_display(summary_json)
    
    return {
        'summary_json': summary_json,
        'formatted_summary': formatted_summary
    }


def generate_guided_tour_for_repo(
    repo_name: str,
    github_token: Optional[str] = None,
    gemini_key: Optional[str] = None,
    max_depth: int = 3
) -> Dict[str, any]:
    """
    Complete pipeline: fetch repo data and generate guided tour.
    
    Args:
        repo_name: Repository in format 'owner/repo'
        github_token: Optional GitHub token
        gemini_key: Optional Gemini API key
        max_depth: Maximum directory depth to traverse
        
    Returns:
        Dictionary with 'tour_json', 'formatted_tour', 'repo_stats', and 'important_files' keys
    """
    # Fetch README
    readme_content = ""
    try:
        readme_content = fetch_readme(repo_name, github_token)
    except FileNotFoundError:
        readme_content = "README.md not found in repository."
    except Exception as e:
        readme_content = f"Error fetching README: {str(e)}"
    
    # Fetch repo tree
    repo_tree = fetch_repo_tree(repo_name, github_token, max_depth=max_depth)
    
    # Identify important files
    important_files = identify_important_files(repo_tree)
    
    # Get stats
    repo_stats = get_repo_summary_stats(repo_tree)
    
    # Generate guided tour
    tour_json = generate_guided_tour(
        repo_name,
        readme_content,
        repo_tree,
        important_files,
        repo_stats,
        gemini_key
    )
    
    # Format for display
    formatted_tour = format_guided_tour(tour_json)
    
    return {
        'tour_json': tour_json,
        'formatted_tour': formatted_tour,
        'repo_stats': repo_stats,
        'important_files': important_files
    }

