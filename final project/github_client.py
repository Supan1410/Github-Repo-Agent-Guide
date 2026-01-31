"""
GitHub API Client
Handles all GitHub repository operations including README fetching and repository structure analysis.
"""

from github import Github
from github.GithubException import GithubException
from typing import Optional, List, Dict


def fetch_readme(repo_name: str, token: Optional[str] = None) -> str:
    """
    Fetch README.md content from a GitHub repository.
    
    Args:
        repo_name: Repository in format 'owner/repo'
        token: Optional GitHub personal access token
        
    Returns:
        README content as string
        
    Raises:
        ValueError: If repo_name format is invalid
        FileNotFoundError: If README.md doesn't exist
        RuntimeError: If repository access fails
    """
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


def fetch_repo_tree(repo_name: str, token: Optional[str] = None, max_depth: int = 3, 
                   skip_dirs: Optional[List[str]] = None) -> List[Dict[str, str]]:
    """
    Fetch repository file/folder structure (tree) from GitHub.
    
    Args:
        repo_name: Repository in format 'owner/repo'
        token: Optional GitHub personal access token
        max_depth: Maximum directory depth to traverse (default: 3)
        skip_dirs: List of directory names to skip (e.g., ['node_modules', '.git'])
        
    Returns:
        List of dictionaries with 'path', 'type' (file/dir), 'name', and 'size' keys
        
    Raises:
        ValueError: If repo_name format is invalid
        RuntimeError: If repository access fails
    """
    if skip_dirs is None:
        skip_dirs = ['.git', 'node_modules', '.venv', 'venv', '__pycache__', 
                     '.pytest_cache', '.mypy_cache', 'dist', 'build', '.next', 
                     'target', '.idea', '.vscode', 'coverage']
    
    if '/' not in repo_name:
        raise ValueError(f"Repository name must be in format 'owner/repo', got '{repo_name}'")
    
    g = Github(token) if token else Github()
    
    owner, repo = repo_name.split('/', 1)
    try:
        repo_obj = g.get_user(owner).get_repo(repo)
    except GithubException as e:
        raise RuntimeError(f"Repository not found or is private. Status: {e.status}")
    
    tree_items = []
    
    def traverse_directory(path: str, depth: int = 0):
        """Recursively traverse directory structure."""
        if depth > max_depth:
            return
        
        try:
            contents = repo_obj.get_contents(path)
            if not isinstance(contents, list):
                contents = [contents]
            
            for item in contents:
                item_name = item.name
                item_path = item.path
                
                # Skip hidden files and directories at root level (except important ones)
                if depth == 0 and item_name.startswith('.') and item_name not in ['.github', '.gitignore', '.env.example']:
                    continue
                
                # Skip excluded directories
                if item.type == 'dir' and item_name in skip_dirs:
                    continue
                
                tree_items.append({
                    'path': item_path,
                    'name': item_name,
                    'type': item.type,
                    'size': item.size if item.type == 'file' else 0
                })
                
                # Recursively traverse subdirectories
                if item.type == 'dir' and depth < max_depth:
                    traverse_directory(item_path, depth + 1)
                    
        except GithubException as e:
            # Skip if directory doesn't exist or access denied
            if e.status != 404:
                pass
    
    # Start traversal from root
    traverse_directory("", 0)
    
    return tree_items


def format_repo_tree(tree_items: List[Dict[str, str]]) -> str:
    """
    Format repository tree items into a readable string representation.
    
    Args:
        tree_items: List of tree item dictionaries
        
    Returns:
        Formatted tree structure as string
    """
    if not tree_items:
        return "No files found in repository."
    
    # Sort items: directories first, then files, both alphabetically
    sorted_items = sorted(tree_items, key=lambda x: (x['type'] != 'dir', x['path'].lower()))
    
    # Build tree structure
    lines = []
    
    for item in sorted_items:
        path = item['path']
        name = item['name']
        item_type = item['type']
        
        # Calculate depth
        depth = path.count('/')
        indent = "  " * depth
        
        # Tree connector
        if depth > 0:
            connector = "├── " if item != sorted_items[-1] else "└── "
        else:
            connector = ""
        
        # Type indicator
        type_indicator = "📁" if item_type == 'dir' else "📄"
        
        lines.append(f"{indent}{connector}{type_indicator} {name}")
    
    return "\n".join(lines)


def identify_important_files(tree_items: List[Dict[str, str]]) -> Dict[str, List[str]]:
    """
    Identify important files in the repository by category.
    
    Args:
        tree_items: List of tree item dictionaries
        
    Returns:
        Dictionary with categories as keys and lists of file paths as values
    """
    important = {
        'documentation': [],
        'dependencies': [],
        'config': [],
        'entry_points': [],
        'ci_cd': [],
        'docker': []
    }
    
    # Patterns for important files
    doc_patterns = ['readme', 'contributing', 'license', 'changelog', 'docs/']
    dep_patterns = ['requirements.txt', 'pyproject.toml', 'package.json', 'poetry.lock', 
                    'yarn.lock', 'package-lock.json', 'Pipfile', 'setup.py', 'setup.cfg',
                    'go.mod', 'go.sum', 'Cargo.toml', 'pom.xml', 'build.gradle']
    config_patterns = ['.env.example', '.gitignore', '.dockerignore', 'config', 'settings',
                       'pytest.ini', 'tox.ini', '.pre-commit-config.yaml']
    entry_patterns = ['main.py', 'app.py', 'server.py', 'index.js', 'index.ts', 'main.ts',
                      'src/main', 'app/main', 'Application.java', 'Main.java']
    ci_patterns = ['.github/workflows', 'ci/', '.gitlab-ci.yml', 'azure-pipelines.yml',
                   'Jenkinsfile', '.travis.yml']
    docker_patterns = ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', '.dockerignore']
    
    for item in tree_items:
        if item['type'] != 'file':
            continue
        
        path_lower = item['path'].lower()
        name_lower = item['name'].lower()
        
        # Check documentation
        if any(pattern in path_lower or pattern in name_lower for pattern in doc_patterns):
            important['documentation'].append(item['path'])
        
        # Check dependencies
        if any(name_lower == pattern or name_lower.endswith(pattern) for pattern in dep_patterns):
            important['dependencies'].append(item['path'])
        
        # Check config
        if any(pattern in path_lower or name_lower == pattern for pattern in config_patterns):
            important['config'].append(item['path'])
        
        # Check entry points
        if any(pattern in name_lower for pattern in entry_patterns):
            important['entry_points'].append(item['path'])
        
        # Check CI/CD
        if any(pattern in path_lower for pattern in ci_patterns):
            important['ci_cd'].append(item['path'])
        
        # Check Docker
        if any(pattern in name_lower for pattern in docker_patterns):
            important['docker'].append(item['path'])
    
    return important


def get_repo_summary_stats(tree_items: List[Dict[str, str]]) -> Dict[str, any]:
    """
    Get summary statistics about the repository structure.
    
    Args:
        tree_items: List of tree item dictionaries
        
    Returns:
        Dictionary with statistics
    """
    total_files = sum(1 for item in tree_items if item['type'] == 'file')
    total_dirs = sum(1 for item in tree_items if item['type'] == 'dir')
    
    # Count files by extension
    extensions = {}
    for item in tree_items:
        if item['type'] == 'file':
            name = item['name']
            if '.' in name:
                ext = name.split('.')[-1].lower()
                extensions[ext] = extensions.get(ext, 0) + 1
    
    # Get top-level directories
    top_level_dirs = [item['name'] for item in tree_items 
                     if item['type'] == 'dir' and '/' not in item['path']]
    
    return {
        'total_files': total_files,
        'total_directories': total_dirs,
        'file_extensions': dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]),
        'top_level_dirs': top_level_dirs
    }

