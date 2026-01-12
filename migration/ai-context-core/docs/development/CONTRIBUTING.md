
# Contributing to AI Context Core

We love your input! We want to make contributing to `ai-context-core` as easy and transparent as possible.

## 🛠️ Development Setup

This project uses `uv` for dependency management, ensuring fast and reliable builds.

1.  **Install uv** (if you haven't):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Clone and Sync**:
    ```bash
    git clone https://github.com/your-org/ai-context-core.git
    cd ai-context-core
    uv sync
    ```

3.  **Run tool locally**:
    ```bash
    uv run ai-ctx --help
    ```

## 🧪 Testing

(To Be Implemented) - We aim for high test coverage using `pytest`.
```bash
uv run pytest
```

## 🎨 Code Style

We use `ruff` to keep the code clean and consistent.

- **Check code**:
    ```bash
    uv run ruff check .
    ```
- **Format code**:
    ```bash
    uv run ruff format .
    ```

## 📝 Commit Messages

We follow the **Conventional Commits** specification. This allows us to automate versioning and changelogs.

Format: `<type>(<scope>): <subject>`

**Types**:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries such as documentation generation

**Example**:
```
feat(cli): add new 'profiles' command to list available configs
fix(engine): resolve timeout issue on large files
docs: update architecture details
```
