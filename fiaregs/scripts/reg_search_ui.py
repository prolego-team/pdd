"""FIA Regulation Search for Formula One

## Key concepts:

- Regulations have been parsed as DocTrees
- DocTrees are simply hierarchical data structures storing text with some metadata
- Some regulations had definition lists that were also extracted
- There are three kinds of searches

    - Quick search: simple semantic search over regulations and definitions
    - Search and summarize: "Quick search" + LLM summary of results
    - Agentic search: Quick search + ability for LLM to follow up/clarify with
      additional questions against the quick search function.

- Regulation search is performed by minimizing the cosine distance between the embedded
  query and the embedded regulation texts.
- Regulation search can be augmented with a cross encoder reranker.
- Definition searches use BM25, since keywords are more important.
- Each query is also scanned for Capitalized Phrases and the definitions are searched
  for a beginning-of-string exact match against the phrases.
"""
import os
from pathlib import Path

import logging
import sys

import gradio as gr

from fiaregs.drivers import setup
from aicore.llm.client import get_llm_client
from aicore.llm import openaiapi as openai

# Suppress a runtime warning re: tokenizer parallelism and multiple threads.
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# === Basic logger setup ===================================================
logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S'
)
logging.getLogger('search').setLevel(logging.DEBUG)
log = logging.getLogger('search')
# ===================================================================

DOC_DIR = Path('data/docs')
DATA_DIR = Path('data')

RERANK = True
PRE_EXPAND = False
POST_EXPAND = True

REGS = {
    '2023 FIA Formula One Sporting Regulations': 'fia_2023_formula_1_sporting_regulations_-_issue_6_-_2023-08-31.yaml',
    '2023 FIA International Sporting Code': '2023_international_sporting_code_fr-en_clean_9.01.2023.yaml',
    '2023 FIA International Sporting Code, Appendix L, Chapter II': 'appendix_l_iii_2023_publie_le_20_juin_2023.yaml',
    '2023 FIA International Sporting Code, Appendix L, Chapter IV': 'appendix_l_iv_2023_publie_le_20_juin_2023.yaml',
    '2023 FIA Formula One Financial Regulations': 'fia_formula_1_financial_regulations_-_issue_16_-_2023-08-31.yaml',
    '2023 FIA Formula One Technical Regulations': 'fia_2023_formula_1_technical_regulations_-_issue_7_-_2023-08-31.yaml'
}

MAX_LLM_CALLS_PER_INTERACTION = 5

DEF_DIVIDER = '\n\n'


def run_demo():

    model_name = 'all-mpnet-base-v2'
    cross_encoder_name = 'cross-encoder/ms-marco-MiniLM-L-12-v2'
    llm_model_name = 'gpt-4'
    llm_api_key = 'OPENAI_API_KEY'
    use_definitions = True
    top_k = 10

    api_client = get_llm_client(llm_api_key)
    llm_model = openai.start_chat(llm_model_name, api_client)

    search, agentic_search, generate_response = setup(
        llm_model,
        DATA_DIR,
        DOC_DIR,
        REGS,
        PRE_EXPAND,
        POST_EXPAND,
        model_name,
        cross_encoder_name,
        top_k,
        use_definitions,
    )

    with gr.Blocks() as demo:
        gr.Markdown('# FIA Regulation Matching')
        question_text = gr.Textbox('Question:', label='Search box', interactive=True)
        with gr.Row():
            quick_search_button = gr.Button('Quick Search')
            search_summarize_button = gr.Button('Search and Summarize')
            deep_search_button = gr.Button('Agentic Search')
        llm_response = gr.Textbox('LLM Response', interactive=False, label='LLM Output')
        regulation_texts = gr.Textbox('Output will appear here', interactive=False, label='Retrieved Documents')
        definition_texts = gr.Textbox('Definitions will appear here', interactive=False, label='Definitions')

        quick_search_button.click(
            fn=search,
            inputs=question_text,
            outputs=[regulation_texts, definition_texts]
        ).then(
            fn=lambda : 'No LLM response requested.',
            inputs=None,
            outputs=llm_response
        )

        search_summarize_button.click(
            fn=search,
            inputs=question_text,
            outputs=[regulation_texts, definition_texts]
        ).then(
            fn= generate_response,
            inputs=[question_text, regulation_texts, definition_texts],
            outputs=llm_response
        )

        deep_search_button.click(
            fn=search,
            inputs=question_text,
            outputs=[regulation_texts, definition_texts]
        ).then(
            fn=agentic_search,
            inputs=[question_text, regulation_texts, definition_texts],
            outputs=llm_response
        )

    demo.queue()
    demo.launch()


if __name__ == '__main__':
    run_demo()
