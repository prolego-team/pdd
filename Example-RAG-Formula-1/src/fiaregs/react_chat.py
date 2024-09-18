"""
Implementation of ReAct agent.
"""
import json
import logging

from collections.abc import Callable, Generator

from aicore.llm import openaiapi as openai

logging.getLogger('react').setLevel(logging.DEBUG)
log = logging.getLogger('react')


FORMAT_MESSAGE = (
    "When the user asks a question, think about what to do before responding. "
    "Share your thoughts with the user so they understand what you are doing. "
    "You can use a function call to get additional information from the user. "
    "When you have the final answer say, \"Final Answer: \" followed by the "
    "response to the user's question."
)


def get_next_message(
        response: openai.AssistantMessage,
        functions: dict[str, Callable]) -> tuple[list[openai.Message], bool]:
    """Get a response to a ReAct LLM call."""

    function_called = False
    return_messages = []
    if response.tool_calls is not None:
        for tool_call in response.tool_calls:
            tcid = tool_call.tool_call_id
            name = tool_call.function_name
            arguments = tool_call.function_args
            results = functions[name](**arguments)
            log.info(f'Function {name}, args = {arguments}')
            return_messages.append(
                openai.ToolMessage(f'Observation: {str(results)}', tcid)
            )

        function_called = True
    else:
        return_messages.append(
            openai.UserMessage(
                ('When you have the answer to my question, please say '
                '"Final Answer:" and then write the final answer.')
            )
        )

    return return_messages, function_called


def make_react_agent(
        system_message: str,
        model: Callable,
        function_descriptions: list[dict],
        functions: dict[str, Callable],
        max_llm_calls: int = 10,
        extra_context: str | None = None,
    ) -> Callable:
    """Return a ReAct agent.

    The agent will answer one question at a time given the tools presented via the
    function_descriptions and functions arguments.

    There is a maximum number of times the LLM (model) may be called, max_llm_calls.
    """

    system_message += FORMAT_MESSAGE

    messages = [openai.SystemMessage(system_message)]

    if extra_context:
        messages.append(
            openai.UserMessage(
                'Additional information that may be useful:\n\n'+extra_context
            )
        )

    def run_once(user_input: str) -> Generator:
        """Engage an LLM ReACT agent to answer a question."""
        input_msg = f'Question: {user_input}'
        messages.append(openai.UserMessage(input_msg))
        yield messages[-1]

        function_call_counter = 0
        for _ in range(max_llm_calls):
            log.info('calling llm')
            response = model(messages, tools=function_descriptions)
            messages.append(response)
            yield messages[-1]

            if response.content and "Final Answer" in response.content:
                break

            next_messages, function_called = get_next_message(
                response,
                functions,
            )
            function_call_counter += function_called

            messages.extend(next_messages)
            yield from next_messages

    return run_once
