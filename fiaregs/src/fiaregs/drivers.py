import os
import re
import json
import logging
import sys
from pathlib import Path
from typing import Callable

from sentence_transformers import CrossEncoder

from aicore.llm import openaiapi as openai
import fiaregs.search.embeddings as emb

from fiaregs.search.semantic_search import cosine_search, rerank
from fiaregs.search.keyword_search import keyword_search, build_index
from fiaregs.search.utils.data_utils import (
    result_to_string,
    get_dict_hash,
    reciprocal_rank_fusion)
from fiaregs.text_utils import get_capitalized_phrases

from fiaregs.utils import (
    load_regs,
    load_defs,
    get_embeddings
)

logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S'
)
logging.getLogger('setup').setLevel(logging.DEBUG)
log = logging.getLogger('setup')


REG_DIVIDER = '\n\n---\n\n'
MAX_LLM_CALLS_PER_INTERACTION = 5

SYSTEM_MESSAGE_BASE = (
    'You are an assitant to a Formula 1 team.  Your job is to answer team questions '
    'to the best of your ability.'
)
SYSTEM_MESSAGE = (
    SYSTEM_MESSAGE_BASE + '  You will be given several excerpts from regulations '
    'to help you in answering.  Some of the provided regulations may be irrelevant, so '
    'ignore these and only use those that appear to be relevant. Do not mention or cite '
    'regulations that are not given to you.  Answer succinctly and make reference to the '
    'relevant regulation sections.\n\n'
    'Think carefully about the question and the provided regulations and definitions. Check that your '
    'response makes sense before answering.'
)

def load_data(doc_dir: Path, reg_map: dict):

    # Load data
    log.info('Loading regulations')
    doc_trees = load_regs(reg_map, doc_dir)
    # import fiaregs.search.utils.doctree as doctree
    # import tiktoken

    # all_regs = ''
    # for dt,tree in doc_trees.items():
    #     all_regs += dt + '\n'
    #     all_regs += doctree.get_tree_text(tree) + '\n\n'

    # encoding = tiktoken.encoding_for_model("gpt-4-0125-preview")
    # print(len(encoding.encode(all_regs)))

    # exit()

    log.info('Loading definitions')
    definitions_flat, definition_ids = load_defs(reg_map, doc_dir)

    return doc_trees, definition_ids, definitions_flat


## Search functions


def make_definition_search(
        definition_ids,
        definitions_flat
    ) -> Callable[[str], list[str]]:

    definition_bm25 = build_index(definitions_flat)

    # Wrapper functions for search and generation
    def search_definitions(query: str) -> list[str]:
        """Do a keyword search over definitions."""
        log.info(f'Searching definitions: {query[:20]}...')
        results = keyword_search(
            definition_bm25,
            query,
            definition_ids,
            definitions_flat,
            5
        )

        results = [
            f'{defn_hit.text} (from {defn_hit.file})' for defn_hit in results
        ]

        return results

    return search_definitions


def make_regulation_search(
        doc_trees,
        embedding_path,
        similarity_model_name,
        cross_encoder_name,
        pre_expand,
        post_expand,
        top_k
    ) -> Callable[[str], list[str]]:

    log.info('Getting encodings for regs')
    model = emb.get_model(similarity_model_name)

    embeddings, flat_texts, flat_ids = get_embeddings(
        doc_trees,
        embedding_path,
        model,
        pre_expand
    )
    log.info(f'Embeddings -- {type(embeddings)} -- {embeddings.shape}')

    rerank_flag = cross_encoder_name is not None
    if rerank_flag:
        rerank_model = CrossEncoder(cross_encoder_name)

    def search_regulations(query: str) -> list[str]:
        """Search regulation embeddings."""
        log.info(f'Searching regulations: {query[:20]}...')
        query_emb = emb.encode(query, model)

        results = cosine_search(query_emb, embeddings, flat_ids, flat_texts, top_k)
        if rerank_flag:
            results = rerank(results, doc_trees, query, rerank_model, post_expand=post_expand)

        # Apply a threshold to results
        if rerank_flag:
            results = [result for result in results if result.reranked_score>-2]
        else:
            results = [result for result in results if result.similarity_score>0.3]
        [print(result) for result in results]
        log.debug(f'Found {len(results)} regulation results.')

        return results

    return search_regulations


def make_compound_search(
        search_regulations,
        search_definitions,
        doc_trees,
        definitions_flat
    ) -> Callable[[str], tuple[str,str]]:

    def search(query: str) -> tuple[str,str]:
        """Do a semantic search over embeddings.  Also return potentially relevant definitiosn."""
        regulation_results = search_regulations(query)
        # regulation_results_str = results_to_string(regulation_results, doc_trees, REG_DIVIDER)

        # Get definitions that may be semantically relevant to the query
        query_definitions = search_definitions(query)
        # query_definitions = [
        #     f'{defn_hit.text} (from {defn_hit.file})' for defn_hit in query_definitions
        # ]
        # log.debug(f'Found {len(query_definitions)} query definitions')

        # Look for capitalized phrases from the regulations in the definitions
        # TODO Could speed this up by storing definitions in a dictionary
        phrase_definitions = []
        for res in regulation_results:
            phrases = set(get_capitalized_phrases(res.text))
            if len(phrases)>0:
                for phrase in phrases:
                    search_phrase = phrase.replace('[','').replace(']','')
                    if len(phrase)>5:
                        defs = [defn for defn in definitions_flat if re.match(f'"?{search_phrase}"?', defn)]
                        phrase_definitions += defs
        phrase_definitions = list(set(phrase_definitions))
        log.debug(f'Found {len(phrase_definitions)} phrase definitions')

        # Look for definitions that may be semantically similar to to the regulation results
        regulation_definitions_set = []
        for result in regulation_results:
            regulation_definitions_set.append(search_definitions(result.text))

        regulation_definitions = reciprocal_rank_fusion(regulation_definitions_set)
        log.debug(f'Found {len(regulation_definitions)} regulation definitions')

        definition_results = list(
            set(regulation_definitions[:5] + phrase_definitions + query_definitions[:2])
        )

        definition_results_str = '\n\n'.join(definition_results)
        regulation_results_str = REG_DIVIDER.join(
            [result_to_string(result, doc_trees) for result in regulation_results]
        )

        return regulation_results_str, definition_results_str

    return search


## Helper function


def build_context(regulations: str | None, definitions: str | None) -> str:
    """Combine regulation and definitions texts for LLM context."""

    context = ''

    if definitions is not None:
        context += (
            'Here are some potentially useful definitions:\n\n'
            f'{definitions}'
            '\n\n---\n\n'
        )

    if regulations is not None:
        context += (
        'Here is potentially useful context from the regulations:\n\n'
        f'{regulations}'
    )

    return context


## Drivers


def driver_llm_only(llm_model: Callable) -> Callable[[str], str]:

    def respond(query: str) -> str:
        log.debug('Calling LLM...')
        messages = [
            openai.SystemMessage(SYSTEM_MESSAGE_BASE),
            openai.UserMessage(query)
        ]
        return llm_model(messages).content

    return respond


def driver_llm_with_search(
        llm_model: Callable,
        data_dir: Path,
        doc_dir: Path,
        reg_map: dict,
        pre_expand: bool,
        post_expand: bool,
        similarity_model_name: str,
        cross_encoder_model_name: str | None,
        top_k: int,
        include_definitions: bool
) -> Callable:

    # Load data
    doc_trees, definition_ids, definitions_flat = load_data(doc_dir, reg_map)

    config = {
        'pre_expand': pre_expand,
        'similarity_model_name': similarity_model_name
    }
    run_id = get_dict_hash(config)
    run_dir = data_dir / Path(str(run_id))
    if not run_dir.exists():
        run_dir.mkdir(parents=True)
        with open(run_dir / 'config.json', 'w') as f:
            json.dump(config, f)

    search_definitions = make_definition_search(definition_ids, definitions_flat)
    search_regulations = make_regulation_search(
        doc_trees,
        run_dir,
        similarity_model_name,
        cross_encoder_model_name,
        pre_expand,
        post_expand,
        top_k
    )
    compound_search = make_compound_search(
        search_regulations,
        search_definitions,
        doc_trees,
        definitions_flat
    )

    def generate_response(question: str) -> str:
        """Generate a simple response."""

        regulations, definitions = compound_search(question)
        if not include_definitions:
            definitions = None
        context = build_context(regulations, definitions)
        prompt = context + f'\n\nHere is the question: {question}'
        messages = [
            openai.SystemMessage(SYSTEM_MESSAGE),
            openai.UserMessage(prompt)
        ]
        log.info('Calling LLM')
        return llm_model(messages).content

    return generate_response


def driver_llm_with_agentic_search(
        llm_model: Callable,
        data_dir: Path,
        doc_dir: Path,
        reg_map: dict,
        pre_expand: bool,
        post_expand: bool,
        similarity_model_name: str,
        cross_encoder_model_name: str | None,
        top_k: int,
        include_definitions: bool
) -> Callable:

    # Load data
    doc_trees, definition_ids, definitions_flat = load_data(doc_dir, reg_map)

    config = {
        'pre_expand': pre_expand,
        'similarity_model_name': similarity_model_name
    }
    run_id = get_dict_hash(config)
    run_dir = data_dir / Path(str(run_id))
    if not run_dir.exists():
        run_dir.mkdir(parents=True)
        with open(run_dir / 'config.json', 'w') as f:
            json.dump(config, f)

    search_definitions = make_definition_search(definition_ids, definitions_flat)
    search_regulations = make_regulation_search(
        doc_trees,
        run_dir,
        similarity_model_name,
        cross_encoder_model_name,
        pre_expand,
        post_expand,
        top_k
    )
    compound_search = make_compound_search(
        search_regulations,
        search_definitions,
        doc_trees,
        definitions_flat
    )

    function_descriptions = [
        {
            'name': 'lookup_definition',
            'description': 'Lookup a word or phrase in the glossary to get its definition.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'A word or phrase for which you want the definition.'
                    },
                },
                'required': ['query']
            }
        },
        {
            'name': 'regulation_search',
            'description': 'Search regulations using semantic search.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'Search query in the form of a question.'
                    },
                },
                'required': ['query']
            }
        }
    ]
    function_descriptions = [{'type': 'function', 'function': func} for func in function_descriptions]
    functions = {
        'lookup_definition': lambda query: '\n\n'.join(search_definitions(query)),
        'regulation_search': lambda query: REG_DIVIDER.join(
            [result_to_string(result, doc_trees) for result in search_regulations(query)]
        )
    }

    def generate_response(question: str) -> str:
        """Generate a simple response."""

        regulations, definitions = compound_search(question)
        if not include_definitions:
            definitions = None

        system_message_new = (
            SYSTEM_MESSAGE +
            '\n\nIf you need additional information, if you need to refine your response, '
            'or if the provided regulations do not appear to answer the question, '
            'you should run additional regulation searches using the `regulation_search` function. '
            'When using this function your queries should rephrase or refine the original '
            'question; don\'t repeat the original question becuase you will get the same results. '
            'You can also look up any word or phrase that you are not sure about using the '
            '`lookup_definition` function.  Repeated tool calls may be necessary to get an '
            'accurate response.  Do your best!'
        )

        context = build_context(regulations, definitions)
        prompt = context + f'\n\nHere is the question: {question}'
        messages = [
            openai.SystemMessage(system_message_new),
            openai.UserMessage(prompt)
        ]

        call_count = 0
        while call_count < MAX_LLM_CALLS_PER_INTERACTION:
            log.info('Calling LLM')
            response = llm_model(messages, tools=function_descriptions)
            messages.append(response)
            if response.tool_calls is None:
                break
            else:
                log.info('Calling tools...')
                try:
                    tool_output_messages = [
                        openai.ToolMessage(
                            str(functions[tool.function_name](**tool.function_args)),
                            tool.tool_call_id)
                        for tool in response.tool_calls
                    ]
                except Exception as e:
                    tool_output_messages = [openai.UserMessage(f'There was a problem calling a tool: {e}')]
                messages += tool_output_messages

        # for message in messages:
        #     print()
        #     print(message)

        return messages[-1].content

    return generate_response


##


# def setup(config: dict):
#     """Setup everything needed for the demo."""
#     data_dir = Path(config['data_dir'])
#     pre_expand = config['pre_expand']
#     post_expand = config['post_expand']
#     rerank_flag = config['rerank']
#     similarity_model_name = config['similarity_model_name']
#     cross_encoder_name = config['cross_encoder_name']
#     llm_model_name = config['llm_model_name']
#     top_k = config['top_k']



#     function_descriptions = [
#         {
#             'name': 'lookup_definition',
#             'description': 'Lookup a word or phrase in the glossary to get its definition.',
#             'parameters': {
#                 'type': 'object',
#                 'properties': {
#                     'query': {
#                         'type': 'string',
#                         'description': 'A word or phrase for which you want the definition.'
#                     },
#                 },
#                 'required': ['query']
#             }
#         },
#         {
#             'name': 'regulation_search',
#             'description': 'Search regulations using semantic search.',
#             'parameters': {
#                 'type': 'object',
#                 'properties': {
#                     'query': {
#                         'type': 'string',
#                         'description': 'Search query in the form of a question.'
#                     },
#                 },
#                 'required': ['query']
#             }
#         }
#     ]
#     function_descriptions = [{'type': 'function', 'function': func} for func in function_descriptions]


#     def generate_response(question: str, regulations: str | None, definitions: str | None) -> str:
#         """Generate a simple response."""
#         log.info('Calling LLM')
#         context = build_context(regulations, definitions)
#         prompt = context + f'\n\nHere is the question: {question}'
#         messages = [
#             openai.SystemMessage(SYSTEM_MESSAGE),
#             openai.UserMessage(prompt)
#         ]
#         return llm_model(messages).content


#     def agentic_search(question: str, regulations: str, definitions) -> str:
#         """Agent-based search."""

#         # Prep agent functions and prompts
#         def regulation_search_wrapper(query):
#             results = search_regulations(query)
#             return REG_DIVIDER.join(
#                 [result_to_string(result) for result in results]
#             )

#         def definition_search_wrapper(query):
#             results = search_definitions(query)
#             return '\n\n'.join(results)

#         functions = {
#             'lookup_definition': definition_search_wrapper,
#             'regulation_search': regulation_search_wrapper
#         }
#         system_message_new = (
#             SYSTEM_MESSAGE +
#             '\n\nIf you need additional information, if you need to refine your response, '
#             'or if the provided regulations do not appear to answer the question, '
#             'you should run additional regulation searches using the `regulation_search` function. '
#             'When using this function your queries should rephrase or refine the original '
#             'question; don\'t repeat the original question becuase you will get the same results. '
#             'You can also look up any word or phrase that you are not sure about using the '
#             '`lookup_definition` function.\n\n'
#             'When you have the answer write "Final Answer:" followed by the response.'
#         )
#         context = build_context(regulations, definitions)
#         agent = make_react_agent(
#             system_message_new,
#             llm_model,
#             function_descriptions,
#             functions,
#             MAX_LLM_CALLS_PER_INTERACTION,
#         )

#         # Agent loop
#         prompt = context + '\n\n' + question
#         status = ''
#         for message in agent(prompt):
#             if message.role=='user':
#                 status = 'User asked a question to the LLM.  Awaiting LLM response...'
#             elif message.role=='tool':
#                 status = 'A search was performed.  Awaiting LLM response...'
#                 log.info('Function call: ' + f'\n\n_<name={message.name}, function_call={message.function_call}>_\n')
#                 response = message.content.replace('Observation: ', '')
#                 if message.name=='regulation_search':
#                     # Add new regulations to exist list
#                     regulations_old = regulations.split(REG_DIVIDER)
#                     regulations_new = response.split(REG_DIVIDER)
#                     regulations = [reg for reg in regulations_new if reg not in regulations_old]
#                     regulations += regulations_old
#                     regulations = REG_DIVIDER.join(regulations)
#                 elif message.name=='lookup_definition':
#                     definitions = response + '\n\n' + definitions
#             elif message.role=='assistant':
#                 if message.content and 'Final Answer:' in message.content:
#                     status = message.content
#                 else:
#                     status = 'The assistant responded.  Awaiting LLM next response...'

#             log.info(status)
#             yield regulations, definitions, status

#     return compound_search, agentic_search, generate_response