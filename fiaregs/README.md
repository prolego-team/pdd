# FIA Regulation Search

> This is a demonstration project only. No guarantees are made with respect to accuracy, stability or reliability.

The FIA RAG application will answer questions on the 2023 FIA Formula One regulations, including sporting, technical and financial regulations.

From the UI there are three modes that you can use:

1. Only search the regulations and do not use the LLM to generate an answer;
2. Search the regulations and then have the LLM generate an appropriate answer;
3. Perform agentic search where the LLM may generate its own searches behind the scene.

The evaluation script uses option 2 by default, but other options can be turned on in the `main` function `scripts/eval.py`. (This is not a "user-editable" option at present.)

## Installation

```bash
python -m venv .venv  # Optional, recommended
source .venv/bin/activate
pip install --upgrade pip
cd fiaregs
pip install .
```

## Demo and Evaluation

To launch the UI:

```bash
python scripts/reg_search_ui.py
```

To run evaluation on the questions/answers in `data/eval_set.json`:

```bash
python scripts/eval.py
```
