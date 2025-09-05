# config.py

import os

# === Repo Settings ===
REPO_PATH = r"C:\Users\RobMo\OneDrive\Documents\th-analysis"
REMOTE_URL = "https://github.com/RobbyMo81/th-analysis.git"
BRANCH = "main"

# === Behavior Flags ===
DRY_RUN = False
MAX_FILE_SIZE_MB = 100

# === Derived Paths ===
README_PATH = os.path.join(REPO_PATH, "README.md")
GITIGNORE_PATH = os.path.join(REPO_PATH, ".gitignore")
LOGS_DIR = os.path.join(REPO_PATH, "logs")
MANIFEST_PATH = os.path.join(LOGS_DIR, "sync_manifest.txt")
COMMIT_LOG_PATH = os.path.join(LOGS_DIR, "commit_log.txt")
POWERBALL_LOG_PATH = os.path.join(LOGS_DIR, "powerball_manifest.txt")

# === Ensure logs directory exists ===
os.makedirs(LOGS_DIR, exist_ok=True)
