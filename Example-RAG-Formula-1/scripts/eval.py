import os
from typing import Callable
from pathlib import Path
import logging
import sys
import time

from datasets import Dataset

from aicore.llm.client import get_llm_client
from aicore.llm import openaiapi as openai
from aicore.llm.tracker import UsageTracker
from aicore.performance.data import Evaluation
from aicore.performance.format import to_excel
from aicore.performance.autoeval import evaluate

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


# === Configuration ========================================================

# Location where data will be stored and location/index of the documents to search
DATA_DIR = Path('data')
DOC_DIR = Path('data/docs')
REGS = {
    '2023 FIA Formula One Sporting Regulations': 'fia_2023_formula_1_sporting_regulations_-_issue_6_-_2023-08-31.yaml',
    '2023 FIA International Sporting Code': '2023_international_sporting_code_fr-en_clean_9.01.2023.yaml',
    '2023 FIA International Sporting Code, Appendix L, Chapter II': 'appendix_l_iii_2023_publie_le_20_juin_2023.yaml',
    '2023 FIA International Sporting Code, Appendix L, Chapter IV': 'appendix_l_iv_2023_publie_le_20_juin_2023.yaml',
    '2023 FIA Formula One Financial Regulations': 'fia_formula_1_financial_regulations_-_issue_16_-_2023-08-31.yaml',
    '2023 FIA Formula One Technical Regulations': 'fia_2023_formula_1_technical_regulations_-_issue_7_-_2023-08-31.yaml'
}

# Retreival parameters
RERANK = True
PRE_EXPAND = False
POST_EXPAND = True
USE_DEFINITIONS = True
TOP_K = 10
DEF_DIVIDER = '\n\n'

# Other configuration
EMBEDDING_MODEL_NAME = 'all-mpnet-base-v2'
CROSS_ENCODER_NAME = 'cross-encoder/ms-marco-MiniLM-L-12-v2'
LLM_MODEL_NAME = 'gpt-4-0125-preview'
LLM_API_KEY = 'OPENAI_API_KEY'
MAX_LLM_CALLS_PER_INTERACTION = 5

EVALUATOR_MODEL_NAME = 'gpt-4o'


def generate_responses(eval_set: Dataset, search: Callable) -> Dataset:
    """Convenience function to generate responses for the entire evaluation set.

    The search function calls the RAG system and returns the response."""

    wait_time = 0
    responses = []
    for query in eval_set['question']:
        responses.append(search(query))
        time.sleep(wait_time)

    return eval_set.add_column('answer', responses)


def main():
    # Setup the LLM model and the evaluation model
    tracker = UsageTracker('llm_tracker')
    api_client = get_llm_client(LLM_API_KEY)
    llm_model = openai.start_chat(LLM_MODEL_NAME, api_client, tracker)
    eval_model = openai.start_chat(EVALUATOR_MODEL_NAME, api_client)

    # Create the RAG function
    # The RAG search function will take a user query and return a response
    # based on the provided documents. There are currently three options,
    # all located in the drivers module:
    # - driver_llm_only: Only uses the LLM, does not search the docs
    # - driver_llm_with_search: Searches the docs and uses the LLM to generate
    #      a response
    # - driver_llm_with_agentic_search: Searches the docs and uses the LLM to
    #      generate a response, but the LLM has the ability to ask follow-up
    #      questions to refine the search.
    search = drivers.driver_llm_with_agentic_search(
        llm_model,
        DATA_DIR,
        DOC_DIR,
        REGS,
        PRE_EXPAND,
        POST_EXPAND,
        EMBEDDING_MODEL_NAME,
        CROSS_ENCODER_NAME,
        TOP_K,
        include_definitions=USE_DEFINITIONS
    )

    # Load the evaluation set
    eval_set = Dataset.from_json('data/eval_set.json', field='eval_set')

    # Generate responses for the evaluation set
    performance_evals = []
    if 'answer' in eval_set.column_names:
        eval_set = eval_set.remove_columns('answer')
    eval_set = generate_responses(eval_set, search)

    # Evaluate the responses and collect data on the LLM usage
    # Here we are using an LLM to evaluate the responses, but the LLM
    # is not always correct, so the evaluation should be inspected for
    # accuracy and consistency.
    for example in eval_set:
        llm_stats = tracker.pop()
        llm_usage = {
            'Input tokens': llm_stats.input_tokens,
            'Generated tokens': llm_stats.generated_tokens,
            'Elapsed time': llm_stats.elapsed_time_sec,
        }
        explanation, score = evaluate(eval_model, example['question'], example['ground_truth'], example['answer'])
        perf_eval = Evaluation(
            task='FIA QA',
            metadata={
                'question': example['question'],
                'context': example['contexts'],
                'eval notes': explanation,
            },
            llm_usage=llm_usage,
            expected=example['ground_truth'],
            actual=example['answer'],
            confidence=score
        )

        performance_evals.append(perf_eval)

    # Save the evaluation results to a file
    to_excel(performance_evals, 'eval_results.xlsx')


if __name__=='__main__':
    main()
