# Project Setup Instructions

## 1. Clone the repository
```bash
git clone <repo-url>
cd research-public
```

## 2. Create a project-wide virtual environment
Prefer python 3.

```bash
python3 -m venv .venv
```

## 3. Activate the virtual environment
```bash
source .venv/bin/activate  # macOS/Linux
# Or
.venv\Scripts\activate     # Windows
```

## 4. Install initial packages
```bash
pip install uv
uv pip install ipykernel
```

- Only install **google-genai** for generative AI. Avoid installing both `google-generativeai` and `google-genai` in the same environment to prevent import errors and confusion!
- Example: To install `google-genai` in a notebook cell (preferred for per-notebook requirements):
  ```python
  !uv pip install -U google-genai
  ```

## 5. Register the virtual environment as a Jupyter kernel
```bash
python -m ipykernel install --user --name=research-project-env
```
- `--name=research-project-env` gives a friendly name visible in notebook kernels.
- Use any meaningful name you like.

## 6. Open any notebook in this repo (any subdirectory) and select the `research-project-env` (or your chosen name) kernel in Cursor.

> If the kernel does not appear, restart Cursor IDE.

## Package usage notes
- For Google GenAI, always use:
  ```python
  import genai
  client = genai.Client()
  ```
- Do NOT use `from google import genai` or `from google.genai import types` — these are old or broken import patterns in the context of `google-genai`.
- Only `ipykernel` is required for Cursor's built-in notebook support.
- No need to install JupyterLab or notebook unless running a separate Jupyter server.
- All team members should use this `.venv` for environment consistency.
