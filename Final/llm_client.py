"""
LLM Client
Handles all LLM operations including README summarization and guided tour generation.
"""

import os
import json
from typing import Optional, Dict, List


def _get_gemini_client(api_key: Optional[str] = None):
    """Get Gemini client instance."""
    try:
        import google.genai as genai
    except ImportError:
        raise RuntimeError("Google GenAI package not installed. Install it with: pip install google-genai")
    
    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Google API key not provided. Set GOOGLE_API_KEY environment variable.")
    
    return genai.Client(api_key=api_key)


def _extract_json_from_response(response_text: str) -> dict:
    """Extract JSON from LLM response, handling markdown or other wrappers."""
    try:
        return json.loads(response_text.strip())
    except json.JSONDecodeError:
        # Try to extract JSON if wrapped in markdown or other text
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            return json.loads(response_text[start_idx:end_idx])
        else:
            raise ValueError("Could not extract JSON from LLM response")


def generate_summary(repo_name: str, readme_content: str, gemini_key: Optional[str] = None) -> str:
    """
    Generate a structured summary of a repository from its README.
    
    Args:
        repo_name: Repository name in format 'owner/repo'
        readme_content: README.md content
        gemini_key: Optional Gemini API key
        
    Returns:
        JSON string containing the summary
    """
    client = _get_gemini_client(gemini_key)
    
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
        summary_json = _extract_json_from_response(response.text)
        return json.dumps(summary_json, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to generate summary: {str(e)}")


def format_summary_for_display(summary_json_str: str) -> str:
    """
    Format the summary JSON into a readable, structured output.
    
    Args:
        summary_json_str: JSON string containing the summary
        
    Returns:
        Formatted string for display
    """
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


def generate_guided_tour(
    repo_name: str,
    readme_content: str,
    repo_tree: List[Dict[str, str]],
    important_files: Dict[str, List[str]],
    repo_stats: Dict[str, any],
    gemini_key: Optional[str] = None
) -> str:
    """
    Generate a guided developer tour using LLM (Gemini).
    
    Args:
        repo_name: Repository name in format 'owner/repo'
        readme_content: README.md content
        repo_tree: List of repository tree items
        important_files: Dictionary of categorized important files
        repo_stats: Repository statistics
        gemini_key: Optional Gemini API key
        
    Returns:
        JSON string containing the guided tour
    """
    from github_client import format_repo_tree
    
    client = _get_gemini_client(gemini_key)
    
    # Format repository tree (limit to reasonable size)
    tree_str = format_repo_tree(repo_tree[:200])  # Limit to first 200 items to avoid token limits
    
    # Format important files
    important_files_str = "\n".join([
        f"  {category.replace('_', ' ').title()}: {', '.join(files[:10])}"  # Limit per category
        for category, files in important_files.items() if files
    ])
    
    # Format stats
    stats_str = f"""
    Total Files: {repo_stats['total_files']}
    Total Directories: {repo_stats['total_directories']}
    Top File Extensions: {', '.join(list(repo_stats['file_extensions'].keys())[:5])}
    Top-Level Directories: {', '.join(repo_stats['top_level_dirs'][:10])}
    """
    
    # Truncate README if too long (keep first 5000 chars)
    readme_preview = readme_content[:5000]
    if len(readme_content) > 5000:
        readme_preview += "\n\n[... README truncated for brevity ...]"
    
    prompt = f"""You are a senior software engineer helping a new developer onboard to a GitHub repository. 
Analyze the following repository information and create a comprehensive, structured guided tour.

Repository: {repo_name}

=== README CONTENT ===
{readme_preview}

=== REPOSITORY STRUCTURE ===
{tree_str}

=== IMPORTANT FILES IDENTIFIED ===
{important_files_str}

=== REPOSITORY STATISTICS ===
{stats_str}

Please provide a JSON response with the following structure:
{{
    "repository_name": "{repo_name}",
    "one_line_summary": "A concise one-sentence description of what this project does",
    "what_it_does": "A 2-3 sentence explanation of the project's purpose and main functionality",
    "key_folders": {{
        "folder_name": "Explanation of what this folder contains and why it's important"
    }},
    "important_files_to_read_first": [
        {{
            "file_path": "path/to/file",
            "reason": "Why this file is important for understanding the project"
        }}
    ],
    "setup_and_run_instructions": "Step-by-step instructions for setting up and running the project (extract from README or infer from structure)",
    "code_organization": "Explanation of how the codebase is organized (architecture pattern, module structure, etc.)",
    "onboarding_path": [
        {{
            "step": 1,
            "action": "What the developer should do in this step",
            "files_to_examine": ["list", "of", "relevant", "files"],
            "learning_goal": "What they should understand after this step"
        }}
    ],
    "technologies_detected": ["list", "of", "technologies", "frameworks", "tools"],
    "testing_approach": "Information about how testing is set up (if detectable)",
    "deployment_info": "Information about deployment/CI-CD setup (if detectable)"
}}

Respond ONLY with the JSON object, no additional text. Make the onboarding_path practical and actionable."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        tour_json = _extract_json_from_response(response.text)
        return json.dumps(tour_json, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to generate guided tour: {str(e)}")


def format_guided_tour(tour_json_str: str) -> str:
    """
    Format the guided tour JSON into a readable, structured output.
    
    Args:
        tour_json_str: JSON string containing the guided tour
        
    Returns:
        Formatted string for display
    """
    try:
        tour = json.loads(tour_json_str)
    except json.JSONDecodeError:
        return tour_json_str
    
    output = []
    output.append("=" * 80)
    output.append(f"🎯 GUIDED DEVELOPER TOUR: {tour.get('repository_name', 'Unknown')}")
    output.append("=" * 80)
    
    # One-line summary
    if tour.get('one_line_summary'):
        output.append(f"\n📌 {tour['one_line_summary']}")
    
    # What it does
    if tour.get('what_it_does'):
        output.append(f"\n📖 What This Project Does:")
        output.append(f"   {tour['what_it_does']}")
    
    # Key folders
    if tour.get('key_folders'):
        output.append(f"\n📁 Key Folders:")
        for folder, explanation in tour['key_folders'].items():
            output.append(f"   • {folder}/")
            output.append(f"     {explanation}")
    
    # Important files
    if tour.get('important_files_to_read_first'):
        output.append(f"\n📄 Important Files to Read First:")
        for file_info in tour['important_files_to_read_first']:
            file_path = file_info.get('file_path', 'Unknown')
            reason = file_info.get('reason', 'Important for understanding the project')
            output.append(f"   • {file_path}")
            output.append(f"     → {reason}")
    
    # Setup and run
    if tour.get('setup_and_run_instructions'):
        output.append(f"\n🚀 Setup and Run Instructions:")
        instructions = tour['setup_and_run_instructions']
        for line in instructions.split('\n'):
            if line.strip():
                output.append(f"   {line}")
    
    # Code organization
    if tour.get('code_organization'):
        output.append(f"\n🏗️  Code Organization:")
        output.append(f"   {tour['code_organization']}")
    
    # Technologies
    if tour.get('technologies_detected'):
        output.append(f"\n🛠️  Technologies Detected:")
        for tech in tour['technologies_detected']:
            output.append(f"   • {tech}")
    
    # Testing approach
    if tour.get('testing_approach'):
        output.append(f"\n🧪 Testing Approach:")
        output.append(f"   {tour['testing_approach']}")
    
    # Deployment info
    if tour.get('deployment_info'):
        output.append(f"\n🚢 Deployment Information:")
        output.append(f"   {tour['deployment_info']}")
    
    # Onboarding path
    if tour.get('onboarding_path'):
        output.append(f"\n🎓 Step-by-Step Onboarding Path:")
        for step_info in tour['onboarding_path']:
            step_num = step_info.get('step', '?')
            action = step_info.get('action', '')
            files = step_info.get('files_to_examine', [])
            goal = step_info.get('learning_goal', '')
            
            output.append(f"\n   Step {step_num}: {action}")
            if files:
                output.append(f"      📂 Files to examine: {', '.join(files)}")
            if goal:
                output.append(f"      🎯 Learning goal: {goal}")
    
    output.append("\n" + "=" * 80)
    
    return "\n".join(output)

