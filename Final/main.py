"""
CLI Entry Point
Command-line interface for the GitHub Repository Guided Tour Generator.
"""

import sys
import os
from dotenv import load_dotenv
from agent import generate_repo_summary, generate_guided_tour_for_repo

load_dotenv()


def parse_arguments():
    """Parse command-line arguments."""
    if len(sys.argv) < 2:
        return None, None, None, 3, 'tour'
    
    repo_name = sys.argv[1]
    github_token = None
    gemini_key = None
    max_depth = 3
    mode = 'tour'  # 'summary' or 'tour'
    
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
        elif sys.argv[i] == "--max-depth" and i + 1 < len(sys.argv):
            try:
                max_depth = int(sys.argv[i + 1])
                if max_depth < 1 or max_depth > 5:
                    print("Warning: max-depth should be between 1 and 5. Using default: 3")
                    max_depth = 3
            except ValueError:
                print("Warning: Invalid max-depth value. Using default: 3")
                max_depth = 3
            i += 2
        elif sys.argv[i] == "--mode" and i + 1 < len(sys.argv):
            mode = sys.argv[i + 1]
            if mode not in ['summary', 'tour']:
                print("Warning: mode must be 'summary' or 'tour'. Using default: 'tour'")
                mode = 'tour'
            i += 2
        else:
            i += 1
    
    return repo_name, github_token, gemini_key, max_depth, mode


def main():
    """Main entry point for the CLI."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <owner/repo> [OPTIONS]")
        print("\nOptions:")
        print("  --github-token TOKEN       GitHub Personal Access Token (for private repos)")
        print("  --github-token-env VAR     Environment variable containing GitHub token")
        print("  --gemini-key KEY           Google Gemini API key (or use GOOGLE_API_KEY env var)")
        print("  --max-depth N              Maximum directory depth to traverse (1-5, default: 3)")
        print("  --mode MODE                Mode: 'summary' (README only) or 'tour' (full analysis, default)")
        print("\nExamples:")
        print("  python main.py streamlit/streamlit")
        print("  python main.py owner/repo --mode summary")
        print("  python main.py owner/repo --gemini-key YOUR_KEY --max-depth 2")
        sys.exit(1)
    
    repo_name, github_token, gemini_key, max_depth, mode = parse_arguments()
    
    if not repo_name:
        print("Error: Repository name required")
        print("Usage: python main.py <owner/repo> [OPTIONS]")
        sys.exit(1)
    
    try:
        if mode == 'summary':
            print(f"📚 Generating summary for: {repo_name}")
            result = generate_repo_summary(
                repo_name=repo_name,
                github_token=github_token,
                gemini_key=gemini_key
            )
            print("\n✅ Summary generated!\n")
            print(result['formatted_summary'])
        else:
            print(f"🔍 Analyzing repository: {repo_name}")
            print(f"📊 Fetching repository structure (max depth: {max_depth})...")
            
            result = generate_guided_tour_for_repo(
                repo_name=repo_name,
                github_token=github_token,
                gemini_key=gemini_key,
                max_depth=max_depth
            )
            
            print("\n✅ Analysis complete!\n")
            print(result['formatted_tour'])
            
            # Optionally show stats
            print("\n" + "=" * 80)
            print("📈 Repository Statistics:")
            print("=" * 80)
            stats = result['repo_stats']
            print(f"Total Files: {stats['total_files']}")
            print(f"Total Directories: {stats['total_directories']}")
            if stats['file_extensions']:
                print(f"Top File Extensions: {', '.join(list(stats['file_extensions'].keys())[:5])}")
            if stats['top_level_dirs']:
                print(f"Top-Level Directories: {', '.join(stats['top_level_dirs'][:10])}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__} - {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

