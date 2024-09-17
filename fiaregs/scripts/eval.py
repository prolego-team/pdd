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
from aicore.performance.data import Evaluation, evaluation_to_dict
from aicore.performance.format import to_excel
from aicore.performance.autoeval import evaluate

from fiaregs import drivers, custom_eval_metrics


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


def generate_responses(eval_set: Dataset, search: Callable) -> Dataset:

    wait_time = 0
    responses = []
    for query in eval_set['question']:
        responses.append(search(query))
        time.sleep(wait_time)

    return eval_set.add_column('answer', responses)


def main():

    model_name = 'all-mpnet-base-v2'
    cross_encoder_name = 'cross-encoder/ms-marco-MiniLM-L-12-v2'
    # cross_encoder_name = None
    # OpenAI
    llm_model_name = 'gpt-4-0125-preview'
    # llm_model_name = 'gpt-3.5-turbo-0125'
    llm_api_key = 'OPENAI_API_KEY'

    # Perplexity
    # llm_model_name = 'mistral-7b-instruct'
    # llm_model_name = 'llama-2-70b-chat'
    # llm_model_name = 'mixtral-8x7b-instruct'
    # llm_api_key = 'PERPLEXITY_API_KEY'

    use_definitions = True
    top_k = 10
    n_runs = 1

    tracker = UsageTracker('llm_tracker')
    api_client = get_llm_client(llm_api_key)
    llm_model = openai.start_chat(llm_model_name, api_client, tracker)
    eval_model = openai.start_chat('gpt-4o', api_client)

    # search = drivers.driver_llm_only(llm_model)
    # search = drivers.driver_llm_with_search(
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
    search = drivers.driver_llm_with_agentic_search(
        llm_model,
        DATA_DIR,
        DOC_DIR,
        REGS,
        PRE_EXPAND,
        POST_EXPAND,
        model_name,
        cross_encoder_name,
        top_k,
        include_definitions=use_definitions
    )

    eval_set = Dataset.from_json('data/eval_set.json', field='eval_set')
    # eval_set = Dataset.from_dict(eval_set[:2])
    print('Original eval set')
    print(eval_set)

    performance_evals = []
    for i in range(n_runs):
        if 'answer' in eval_set.column_names:
            eval_set = eval_set.remove_columns('answer')
        eval_set = generate_responses(eval_set, search)
        print('New evaluation set')
        print(eval_set)

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

    to_excel(performance_evals, 'eval_results.xlsx')


if __name__=='__main__':
    main()