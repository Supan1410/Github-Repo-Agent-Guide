"""
Streamlit Web Application
Interactive web UI for the GitHub Repository Guided Tour Generator.
"""

import streamlit as st
import os
from typing import Tuple
from dotenv import load_dotenv
from agent import generate_repo_summary, generate_guided_tour_for_repo

load_dotenv()


def validate_repo_format(repo_name: str) -> Tuple[bool, str]:
    """Validate repository name format."""
    if not repo_name:
        return False, "Repository name cannot be empty"
    
    if '/' not in repo_name:
        return False, "Repository must be in format 'owner/repo' (e.g., 'streamlit/streamlit')"
    
    parts = repo_name.split('/')
    if len(parts) != 2:
        return False, "Repository must be in format 'owner/repo'"
    
    if not parts[0].strip() or not parts[1].strip():
        return False, "Owner and repository name cannot be empty"
    
    return True, ""


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="GitHub Repo Guided Tour Generator",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title and description
    st.title("🎯 GitHub Repository Guided Tour Generator")
    st.markdown("""
    This AI-powered tool analyzes any public GitHub repository and generates comprehensive 
    guided tours to help new developers understand the codebase quickly.
    
    **How it works:**
    1. Enter a repository in the format `owner/repo` (e.g., `streamlit/streamlit`)
    2. Choose analysis mode (Summary or Full Guided Tour)
    3. Click "Generate" to analyze the repository
    4. Get a structured onboarding guide with step-by-step instructions
    """)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        analysis_mode = st.radio(
            "Analysis Mode",
            ["Full Guided Tour", "README Summary Only"],
            help="Full Tour analyzes README + repo structure. Summary only analyzes README."
        )
        
        max_depth = st.slider(
            "Maximum Directory Depth",
            min_value=1,
            max_value=5,
            value=3,
            help="How deep to traverse the repository structure (only for Full Tour)",
            disabled=(analysis_mode == "README Summary Only")
        )
        
        st.markdown("---")
        st.markdown("### 📚 Example Repositories")
        example_repos = [
            "streamlit/streamlit",
            "pallets/flask",
            "tiangolo/fastapi",
            "django/django"
        ]
        
        for repo in example_repos:
            if st.button(f"📦 {repo}", key=f"example_{repo}", use_container_width=True):
                st.session_state.repo_input = repo
    
    # Main input section
    st.header("🔍 Repository Input")
    
    # Initialize session state
    if 'repo_input' not in st.session_state:
        st.session_state.repo_input = ""
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    if 'last_repo' not in st.session_state:
        st.session_state.last_repo = None
    if 'last_mode' not in st.session_state:
        st.session_state.last_mode = None
    
    # Repository input
    repo_name = st.text_input(
        "Enter GitHub Repository",
        value=st.session_state.repo_input,
        placeholder="owner/repo (e.g., streamlit/streamlit)",
        help="Enter the repository in the format: owner/repository-name"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        analyze_button = st.button("🚀 Generate", type="primary", use_container_width=True)
    
    with col2:
        if st.session_state.last_result:
            if st.button("🔄 Clear Results", use_container_width=True):
                st.session_state.last_result = None
                st.session_state.last_repo = None
                st.session_state.last_mode = None
                st.rerun()
    
    # Validate input
    if analyze_button:
        is_valid, error_msg = validate_repo_format(repo_name)
        
        if not is_valid:
            st.error(f"❌ Invalid repository format: {error_msg}")
        else:
            # Get API keys from environment
            github_token = os.getenv("GITHUB_TOKEN")
            gemini_key = os.getenv("GOOGLE_API_KEY")
            
            if not gemini_key:
                st.error("""
                ⚠️ **Google API Key Required**
                
                Please set the `GOOGLE_API_KEY` environment variable or create a `.env` file with:
                ```
                GOOGLE_API_KEY=your_api_key_here
                ```
                """)
            else:
                # Generate analysis
                mode = "summary" if analysis_mode == "README Summary Only" else "tour"
                
                with st.spinner(f"🔍 Analyzing repository {repo_name}... This may take a moment."):
                    try:
                        if mode == "summary":
                            result = generate_repo_summary(
                                repo_name=repo_name,
                                github_token=github_token,
                                gemini_key=gemini_key
                            )
                            result['mode'] = 'summary'
                        else:
                            result = generate_guided_tour_for_repo(
                                repo_name=repo_name,
                                github_token=github_token,
                                gemini_key=gemini_key,
                                max_depth=max_depth
                            )
                            result['mode'] = 'tour'
                        
                        st.session_state.last_result = result
                        st.session_state.last_repo = repo_name
                        st.session_state.last_mode = mode
                        st.success("✅ Analysis complete!")
                        
                    except FileNotFoundError as e:
                        st.error(f"❌ **Repository Error:** {str(e)}")
                    except ValueError as e:
                        st.error(f"❌ **Validation Error:** {str(e)}")
                    except RuntimeError as e:
                        st.error(f"❌ **Runtime Error:** {str(e)}")
                    except Exception as e:
                        st.error(f"❌ **Unexpected Error:** {type(e).__name__} - {str(e)}")
                        st.exception(e)
    
    # Display results
    if st.session_state.last_result:
        st.markdown("---")
        result = st.session_state.last_result
        mode = result.get('mode', 'tour')
        
        if mode == 'summary':
            st.header(f"📖 Repository Summary: {st.session_state.last_repo}")
            st.markdown(result['formatted_summary'])
            
            with st.expander("📄 Raw JSON"):
                st.code(result['summary_json'], language="json")
        else:
            st.header(f"📖 Guided Tour: {st.session_state.last_repo}")
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["🎯 Guided Tour", "📊 Repository Stats", "📄 Raw JSON"])
            
            with tab1:
                # Display formatted guided tour
                st.markdown(result['formatted_tour'])
            
            with tab2:
                st.subheader("Repository Statistics")
                stats = result['repo_stats']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Files", stats['total_files'])
                    st.metric("Total Directories", stats['total_directories'])
                
                with col2:
                    if stats['file_extensions']:
                        st.subheader("Top File Extensions")
                        for ext, count in list(stats['file_extensions'].items())[:10]:
                            st.text(f"{ext}: {count} files")
                
                if stats['top_level_dirs']:
                    st.subheader("Top-Level Directories")
                    for dir_name in stats['top_level_dirs'][:10]:
                        st.text(f"📁 {dir_name}/")
                
                # Important files
                important_files = result['important_files']
                if any(important_files.values()):
                    st.subheader("Important Files by Category")
                    for category, files in important_files.items():
                        if files:
                            with st.expander(f"{category.replace('_', ' ').title()} ({len(files)} files)"):
                                for file_path in files[:20]:  # Limit display
                                    st.text(f"📄 {file_path}")
            
            with tab3:
                st.subheader("Raw JSON Output")
                st.code(result['tour_json'], language="json")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Built with ❤️ using Streamlit, PyGithub, and Google Gemini</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

