# optional cli entry point
# setup.py

from setuptools import setup, find_packages

setup(
    name="repo_sync_agent",
    version="1.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["sync-repo = repo_sync_agent:main"]},
    install_requires=[],
    author="Rob",
    description="Agentic CLI tool for repo hygiene, audit, and lucky number generation",
)
