
# Quick Start Guide

Follow these steps to set up `ai-context-core` as a standalone repository.

## 1. Move and Isolate
Move the folder to your projects directory (outside the current project).

```bash
# Example: move to your projects folder
mv migration/ai-context-core ~/projects/ai-context-core
cd ~/projects/ai-context-core
```

## 2. Initialize Git
Set up version control for the new repository.

```bash
git init
# Create basic .gitignore if it doesn't exist
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".venv/" >> .gitignore
echo ".ai-context/" >> .gitignore
echo "dist/" >> .gitignore
echo "analysis_results/" >> .gitignore

git add .
git commit -m "feat: initial commit of ai-context-core structure"
```

## 3. Install Dependencies
Use `uv` to create the virtual environment and install the package in editable mode.

```bash
# Create venv and install dependencies defined in pyproject.toml
uv venv
uv sync
```
*Note: If you prefer standard pip: `python3 -m venv .venv && source .venv/bin/activate && pip install -e .`*

## 4. Verification (Smoke Test)
Verify that the CLI is installed correctly.

```bash
# Should show CLI help
uv run ai-ctx --help
```

## 5. First Run ("Dogfooding")
Use the tool to analyze itself. This will initialize the AI context within the `ai-context-core` repo itself.

```bash
# 1. Initialize context (using generic profile)
uv run ai-ctx init --profile generic

# 2. Run first analysis
uv run ai-ctx analyze
```

If successful, you will see a generated `.ai-context/` folder with the initial report. You are now ready to push to GitHub/GitLab!
