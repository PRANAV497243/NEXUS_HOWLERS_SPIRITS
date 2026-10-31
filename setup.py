"""
PROJECT NEXUS — Setup Configuration
Developed by Pranav, AI & DE Branch
"""
from setuptools import setup, find_packages

setup(
    name="project-nexus",
    version="1.0.0",
    description="PROJECT NEXUS — Autonomous Multi-Agent AI Problem Solver",
    author="Developed by Pranav, AI & DE Branch",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "langgraph>=0.2.0",
        "langchain>=0.3.0",
        "langchain-community>=0.3.0",
        "pydantic>=2.5.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "streamlit>=1.38.0",
        "chromadb>=0.5.0",
        "matplotlib>=3.8.0",
        "pandas>=2.1.0",
        "python-dotenv>=1.0.0",
        "tavily-python>=0.5.0",
    ],
)
