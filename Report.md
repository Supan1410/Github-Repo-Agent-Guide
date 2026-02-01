GitHub Repository Guided Tour Generator - Project Report

Executive Summary
I developed an AI-powered tool designed to streamline developer onboarding by generating intelligent "guided tours" of GitHub repositories. By integrating the GitHub API for structural analysis and Google Gemini for semantic understanding, the system provides a structured roadmap for any public codebase, reducing the time required for a new developer to become productive.

1. Project Motivation
Onboarding to a new project often involves navigating complex directory trees and deciphering dense documentation. I built this tool to automate the discovery phase of development, transforming raw file structures into actionable, prioritized reading lists that explain the why behind the code.

2. Implementation Journey
The project was developed in four distinct phases:

API Integration: I built a custom GitHub client using PyGithub to handle recursive tree traversal and README fetching.

LLM Orchestration: I integrated the Google Gemini API to process repository metadata. This involved significant prompt engineering to ensure the AI acts as a technical architect rather than a general assistant.

Formatting Layer: I developed logic to convert raw LLM JSON outputs into human-readable, formatted reports with clear hierarchy and iconography.

Dual Interface Deployment: I finalized the project by providing both a CLI tool for power users and a Streamlit web application for a more visual, interactive experience.

3. System Architecture
The project follows a modular, layered architecture pattern. This ensures separation of concerns, making the codebase easier to maintain and test.

github_client.py: Manages all external communication with GitHub. It handles rate limiting, authentication, and directory filtering.

llm_client.py: Handles communication with Gemini. It includes robust error handling for JSON extraction and prompt management.

agent.py: Acts as the controller, managing the flow of data from GitHub to the AI and ensuring the final output is properly structured.

app.py & main.py: The entry points for the web and CLI interfaces, respectively.

4. Technical Deep-Dive
4.1 Structural Analysis & Filtering One of the core challenges was managing the "noise" in large repositories. I implemented:

Recursive Traversal with Depth Limits: Prevents the system from being overwhelmed by massive projects by limiting scans (defaulting to depth 3).

Exclusion Logic: Automatically skips irrelevant directories like .git, node_modules, dist, and build caches.

Categorization: I used pattern matching to identify key files like CI/CD workflows, Docker configurations, and dependency manifests.

4.2 AI Prompting & JSON Sanitization To ensure the output was both useful and machine-readable, I:

Enforced a strict JSON schema for the AI's response to ensure consistency.

Implemented a "Senior Engineer" persona for the model to ensure the "Onboarding Path" was technically accurate and prioritized.

Built a regex-based extraction utility to clean LLM responses that might accidentally include markdown formatting or conversational filler.

5. Key Features Delivered
Full Guided Tour: Provides a one-line summary, key folder explanations, and an "Onboarding Path" (the specific order in which files should be read to understand the logic).

Repository Statistics: Generates metrics on file counts, directory depth, and the most common file extensions found in the project.

README Summarization: Offers a high-level overview for a quick "TL;DR" of a project’s purpose and tech stack.

Interactive Web UI: A tabbed interface in Streamlit that allows users to toggle between the tour, repository stats, and raw data.

6. Technology Stack
Core Logic: Python 3

AI Integration: google-genai (Gemini-1.5-Flash)

API Management: PyGithub

Frontend: Streamlit

Environment: python-dotenv

7. Challenges Overcome
API Rate Limits: I implemented optional token support to allow for 5,000 requests per hour versus the 60 allowed for unauthenticated users.

Context Window Limits: For very large repositories, I implemented data truncation and intelligent filtering to ensure only the most relevant structure is sent to the LLM, staying within token limits without losing context.

8. Conclusion
This project successfully bridges the gap between raw source code and developer understanding. By automating the architectural analysis of a repository, I have created a tool that provides immediate value to any developer exploring open-source software or joining a new team.