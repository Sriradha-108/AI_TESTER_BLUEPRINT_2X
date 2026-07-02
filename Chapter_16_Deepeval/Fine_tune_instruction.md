# Ask-the-Repo: Local AI Assistant Setup Guide

This tool lets you ask questions about our code repository and get answers
from an AI model that runs **entirely on your own computer** — no internet
account, no data leaves your machine.

Follow the steps below in order. It takes about 15–20 minutes the first time.

---

## What you need before starting

- A laptop or desktop (Windows, macOS, or Linux)
- About 5 GB of free disk space
- Python installed (version 3.9 or newer)
  - Check by opening a terminal and typing: `python --version`
  - If you don't have it, download it from https://www.python.org/downloads/

---

## Step 1 — Install Ollama (the AI engine)

Ollama is the free program that runs the AI model on your computer.

1. Go to https://ollama.com/download
2. Download the version for your system and install it like any normal app.
3. After installing, open a terminal and type this to confirm it works:

   ```
   ollama --version
   ```

   If you see a version number, you're good.

---

## Step 2 — Download the AI models

In your terminal, run these two commands one at a time. Each one downloads a
model, so give them a few minutes.

```
ollama pull ministral
ollama pull nomic-embed-text
```

- `ministral` is the model that writes the answers.
- `nomic-embed-text` is a small helper model that lets the tool search the code.

> If `ministral` doesn't download, ask your instructor for the exact model
> name to use, then run `ollama pull <that-name>`.

---

## Step 3 — Get the tool and the code

1. Copy the folder your instructor shared with you (it contains `repo_qa.py`)
   to somewhere easy to find, like your Desktop.
2. Open a terminal **inside that folder**.
3. Download the code repository we'll be asking about:

   ```
   git clone https://github.com/PramodDutta/Advance-Playwright-Framework
   ```

   > No `git`? Install it from https://git-scm.com/downloads, or ask your
   > instructor for a zipped copy of the repo instead.

---

## Step 4 — Install the two Python packages

In the same terminal:

```
pip install ollama chromadb
```

---

## Step 5 — Build the search index (do this once)

This step reads the whole repository so the AI can find answers in it.

```
python repo_qa.py index --repo ./Advance-Playwright-Framework --model ministral
```

Wait until it prints **"Done."** You only need to do this again if the code
changes.

---

## Step 6 — Ask your questions!

To ask one question:

```
python repo_qa.py ask --model ministral -q "How do I run the tests?"
```

To have a back-and-forth conversation instead:

```
python repo_qa.py ask --model ministral
```

Then just type your questions. Type `exit` when you're finished.

---

## Tips

- Ask specific questions ("How is the login page tested?") rather than vague
  ones ("Explain everything.").
- The AI answers using the actual code, and it will tell you which files it
  looked at.
- It's a small model, so it can make mistakes. Always double-check important
  answers against the real code.

---

## Something not working?

| Problem | Try this |
|---|---|
| `command not found: ollama` | Ollama isn't installed — redo Step 1. |
| `No index found` | You skipped Step 5 — run the `index` command. |
| Model name error | Run `ollama list` to see your exact model name and use that. |
| Answers seem off-topic | Add `-k 10` to the end of your `ask` command to search more code. |

If you're still stuck, contact your instructor with a screenshot of the error.
