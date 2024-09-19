"""
FIA Regulation Search for Formula One
"""
import os
from pathlib import Path
import logging
import sys

from aicore.llm.client import get_llm_client
from aicore.llm import openaiapi as openai
from aicore.llm.tracker import UsageTracker

from fiaregs import drivers


# Suppress a runtime warning re: tokenizer parallelism and multiple threads.
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# === Basic logger setup ===================================================
logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S'
)
logging.getLogger(__name__).setLevel(logging.DEBUG)
log = logging.getLogger(__name__)
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
    # cross_encoder_name = None
    # OpenAI
    llm_model_name = 'gpt-4-0125-preview'
    # llm_model_name = 'gpt-3.5-turbo-0125'
    llm_api_key = 'OPENAI_API_KEY'
    # Perplexity
    # llm_model_name = 'mistral-7b-instruct'
    # llm_api_key = 'PERPLEXITY_API_KEY'

    use_definitions = True
    top_k = 10

    api_client = get_llm_client(llm_api_key)
    llm_model = openai.start_chat(llm_model_name, api_client)

    # TODO pretty print messages to terminal

    # search = drivers.driver_llm_only(llm_model)
    search = drivers.driver_llm_with_search(
        llm_model,
        DATA_DIR,
        DOC_DIR,
        REGS,
        PRE_EXPAND,
        POST_EXPAND,
        model_name,
        cross_encoder_name,
        top_k,
        include_definitions=True
    )
    # search = drivers.driver_llm_with_agentic_search(
    #     llm_model,
    #     DATA_DIR,
    #     DOC_DIR,
    #     REGS,
    #     PRE_EXPAND,
    #     POST_EXPAND,
    #     model_name,
    #     cross_encoder_name,
    #     top_k,
    #     include_definitions=use_definitions
    # )

    while (query := input('Question: ')) != 'quit':
        print(search(query))


if __name__ == '__main__':
    run_demo()
