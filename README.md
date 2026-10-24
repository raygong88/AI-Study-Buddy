# 🎓 AI Study Buddy

**CS4680 Assignment 3 — AI Assistant Project**

AI Study Buddy is a Python/Streamlit web app that helps college students understand CS concepts, generate personalized multiple-choice questions, check quiz answers, and refine explanations based on feedback.

## The problem and our solution

Students often need explanations adapted to their current knowledge and immediate practice to see if they understand a topic. This MVP brings both into one simple interface. Unlike a plain static website, **Local Ollama (FREE)** uses the Ollama HTTP API on the same computer to generate original explanations and structured quizzes. An optional OpenAI API mode is also available.

## Features

- **Explain a Concept:** Choose any topic and difficulty level.
- **Iterative Refinement:** Request a simpler, shorter, or more example-driven explanation, or submit custom feedback.
- **Practice Quiz:** Generate 3–5 multiple-choice questions, answer them, and receive deterministic scoring and explanations.
- **Download Notes:** Save an explanation as a text file.
- **Local Ollama Mode (FREE):** Generate real responses through an installed Qwen model without a cloud API key.
- **Preview Mode:** Explore a fixed TCP handshake example. Preview responses are **not** live AI outputs.

## Technology

- Python 3.11+ (recommended)
- [Streamlit](https://streamlit.io/) for the user interface
- [Ollama](https://ollama.com/) local API (`http://127.0.0.1:11434/api/chat`) and a downloaded model, default `qwen3.5:9b`
- Optional: [OpenAI Python SDK](https://github.com/openai/openai-python) / Responses API, model `gpt-4.1-mini` (usage billed separately)
- Python unit tests for output validation and grading

## macOS setup (MacBook / iMac)

1. Install Python 3.11 or newer from [python.org/macOS](https://www.python.org/downloads/macos/) if needed.
2. Download and extract the project ZIP to your **Downloads** or **Desktop** folder.
3. Open the extracted `AI_Study_Buddy` folder and double-click **`RUN_MAC.command`**. If macOS does not allow launching the script by double-clicking, open **Terminal**, type `bash ` (with a space), drag `RUN_MAC.command` into the Terminal window, and press Return.
4. The script creates a virtual environment and installs dependencies on the first run. Wait for the installation to complete; the web app should appear at `http://localhost:8501`.
5. To use real AI for free, install and start **Ollama** (https://ollama.com/download) and download your model (`ollama pull qwen3.5:9b`). Leave Ollama running. The sidebar will offer **Local Ollama (FREE)**. Select it to generate real output. No `.env` or API key required.
6. Optional paid cloud mode: create `.env` from `.env.example`, set `OPENAI_API_KEY`, restart, and choose **OpenAI API (paid)**.
7. **Preview only** is a scripted example, not a working LLM demo.

**Manual Mac launch from the project directory:**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

If your `python3` is too old, install Python 3.11+ and replace `python3` with the installed interpreter (for example `python3.13`). For some Mac setups, installing Apple's command-line developer tools using `xcode-select --install` may be necessary for package installation.

## Windows setup

1. Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/). Enable the option to add Python to PATH if prompted.
2. Download and extract the project ZIP.
3. Double-click **`RUN_WINDOWS.bat`** inside the extracted folder. It automatically creates a virtual environment and installs packages. A browser should open at `http://localhost:8501`.
4. For free local real AI, install and launch Ollama and download `qwen3.5:9b`. Select **Local Ollama (FREE)**.
5. Or use **Preview only** (fixed content, not live AI). Optional paid OpenAI mode: copy `.env.example` to `.env`, set `OPENAI_API_KEY`, and select **OpenAI API (paid)**.

**Alternative command-line start (PowerShell, from the project folder):**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**macOS/Linux:**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Stop with **Ctrl+C** in the terminal.

## Free local AI with Ollama (recommended for CS4680)

1. Start the Ollama desktop app. In Terminal, run `ollama list` to confirm `qwen3.5:9b` is installed. If not, run `ollama pull qwen3.5:9b` (downloads several GB).
2. To verify that local server is listening, open `http://localhost:11434/api/tags` in a browser; it should display installed models.
3. Run AI Study Buddy, choose **Local Ollama (FREE)**, explain a concept, generate a quiz, and refine an explanation. Local inference uses Mac resources and no per-request API charges.
4. For classroom presentations, keep Ollama open and plug your Mac into power. Model generation speed depends on hardware. The local server runs on the same machine; do not assume a public Streamlit deployment can access your Mac's localhost.

## Optional paid OpenAI mode: How to get an API key

Create/manage your key at https://platform.openai.com/api-keys. API usage is billed separately from a ChatGPT subscription and a payment method/credits may be needed. Protect the key and set usage limits in your API account.

**Security:** `.env` and `.streamlit/secrets.toml` are git-ignored. Never commit, paste publicly, or include an API key in a screen recording. A deployment can use `OPENAI_API_KEY` as an environment variable or Streamlit Secrets.

## Prompt engineering techniques (meets course requirement)

| Pattern | Where it is used | Benefit |
|---|---|---|
| **Persona** | `TUTOR_PERSONA` and `QUIZ_PERSONA` in `prompts.py` | Adapts a consistent teaching role; avoids unsupported claims |
| **Few-Shot** | `FEW_SHOT_EXPLANATIONS` and `FEW_SHOT_QUIZ` in `prompts.py` | Demonstrates concise teaching structure and quiz style |
| **Iterative Refinement** | `refinement_input` in `prompts.py` | Uses previous output and student feedback to improve clarity |

The quiz uses a strict JSON schema (see `ai_engine.py`) and Python checks answer keys and computes scores locally.

## Flow and architecture

```text
Student → Streamlit web UI → Persona + Few-Shot prompt → Ollama local API / OpenAI API
                                                      ↓
Student ← Explanation / Quiz ← Validated AI response ←─┘

Student feedback → Prior explanation + feedback → local Ollama / OpenAI → Refined explanation
Quiz answers → Local Python grade_quiz() → Score and teaching explanations
```

## How to test

Run unit tests:

```bash
python -m unittest discover -s tests -v
```

Manual live test:

1. Start Ollama and run in **Local Ollama (FREE)** mode; alternatively use the paid OpenAI mode.
2. Enter **TCP Three-Way Handshake**, choose **Computer Science Student**, click **Explain Topic**.
3. Click **Make it simpler** to show iterative refinement.
4. Open **Practice Quiz**, create 3 questions, answer them, and submit.
5. Show the sidebar's **Prompt Engineering Patterns** and the **How AI Works** tab.

**Note:** A real LLM must be used for the live demo; free local Ollama satisfies this without a paid key. Preview-only mode is not sufficient for the assignment's working-LLM requirement. AI content may contain mistakes; verify technical details against the course material.

## GitHub submission

Create a GitHub repository such as `ai-study-buddy`, upload project source files, verify `.env` and `.venv` were **not** uploaded, and include this README. Submit the repo URL along with the published video link using the course form.

## Video and presentation

See [`PRESENTATION_GUIDE.md`](PRESENTATION_GUIDE.md) for a 90-second classroom script, a sample live demo flow, and a <2-minute vertical short-video plan.

## Future improvements

Upload course PDFs, add spaced-repetition reminders, track learner progress over time, and support more subjects. These are **future ideas**, not implemented features.
