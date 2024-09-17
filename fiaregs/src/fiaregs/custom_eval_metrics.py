from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

import numpy as np

from ragas.llms.json_load import json_loader
from ragas.llms.prompt import Prompt
from ragas.metrics._answer_similarity import AnswerSimilarity
from ragas.metrics.base import EvaluationMode, MetricWithEmbeddings, MetricWithLLM
from ragas.run_config import RunConfig

if t.TYPE_CHECKING:
    from langchain_core.callbacks import Callbacks

CORRECTNESS_PROMPT = Prompt(
    name="answer_correctness",
    instruction="""Extract following from given question and ground truth
            "TP": statements that are present in both the answer and the ground truth,
            "FP": statements present in the answer but not found in the ground truth,
            "FN": relevant statements found in the ground truth but omitted in the answer,
        """,
    examples=[
        {
            "question": """What powers the sun and what is its primary function?""",
            "answer": """The sun is powered by nuclear fission, similar to nuclear reactors on Earth, and its primary function is to provide light to the solar system.""",
            "ground_truth": """The sun is actually powered by nuclear fusion, not fission. In its core, hydrogen atoms fuse to form helium, releasing a tremendous amount of energy. This energy is what lights up the sun and provides heat and light, essential for life on Earth. The sun's light also plays a critical role in Earth's climate system and helps to drive the weather and ocean currents.""",
            "Extracted statements": {
                "TP": ["The sun's primary function is to provide light"],
                "FP": [
                    "The sun is powered by nuclear fission",
                    "similar to nuclear reactors on Earth",
                ],
                "FN": [
                    "The sun is powered by nuclear fusion, not fission",
                    "In its core, hydrogen atoms fuse to form helium, releasing a tremendous amount of energy",
                    "This energy provides heat and light, essential for life on Earth",
                    "The sun's light plays a critical role in Earth's climate system",
                    "The sun helps to drive the weather and ocean currents",
                ],
            },
        },
        {
            "question": """What is the boiling point of water?""",
            "answer": """The boiling point of water is 100 degrees Celsius at sea level.""",
            "ground_truth": """The boiling point of water is 100 degrees Celsius (212 degrees Fahrenheit) at sea level, but it can change with altitude.""",
            "Extracted statements": {
                "TP": [
                    "The boiling point of water is 100 degrees Celsius at sea level"
                ],
                "FP": [],
                "FN": [
                    "The boiling point can change with altitude",
                    "The boiling point of water is 212 degrees Fahrenheit at sea level",
                ],
            },
        },
    ],
    input_keys=["question", "answer", "ground_truth"],
    output_key="Extracted statements",
    output_type="json",
)


BINARY_CORRECTNESS_PROMPT = Prompt(
    name="binary_answer_correctness",
    instruction="""Determine if a "generated_answer" is a correct response to a "question".  The "truth" is also given to you.  If the "generated_answer" includes the "truth", then respond "True", otherwise respond with "False".  It is okay if the "generated_answer" includes additional information.,
        """,
    examples=[
        {
            "question": """What is the boiling point of water?""",
            "generated_answer": """The boiling point of water is 100 degrees Celsius at sea level and 212 degrees Farenheit at sea level.  These values change with altitude.""",
            "truth": """The boiling point of water is 100 degrees Celsius.""",
            "Evaluator Response": """True.""",
        },
        {
            "question": """What is the minimum age required to be president of the United States?""",
            "generated_answer": """The minimum age to be president is 35, unless the provisions of the Lead Leader Act of 1974 take precedence.""",
            "truth": """There is no minimum age to be president.""",
            "Evaluator Response": """False.""",
        },
    ],
    input_keys=["question", "generated_answer", "truth"],
    output_key="Evaluator Response",
    output_type="str",
)


@dataclass
class AnswerCorrectness(MetricWithLLM, MetricWithEmbeddings):

    """
    Measures answer correctness compared to ground truth as a combination of
    factuality and semantic similarity.

    Attributes
    ----------
    name: string
        The name of the metrics
    weights:
        a list of two weights corresponding to factuality and semantic similarity
        Defaults [0.75, 0.25]
    answer_similarity:
        The AnswerSimilarity object
    """

    name: str = "answer_correctness"  # type: ignore[reportIncompatibleMethodOverride]
    evaluation_mode: EvaluationMode = EvaluationMode.qga  # type: ignore[reportIncompatibleMethodOverride]
    correctness_prompt: Prompt = field(default_factory=lambda: CORRECTNESS_PROMPT)
    weights: list[float] = field(default_factory=lambda: [0.75, 0.25])
    answer_similarity: AnswerSimilarity | None = None

    def __post_init__(self: t.Self):
        if len(self.weights) != 2:
            raise ValueError(
                "Expects a list of two weights. First for factuality, second for semantic similarity"
            )
        if all([w == 0 for w in self.weights]):
            raise ValueError("At least one weight must be non-zero")
        if not all([w >= 0 for w in self.weights]):
            raise ValueError("Weights must be non-negative")

        self.log = ''

    def __del__(self):
        with open('metric_answer_correctness_log.txt', 'w') as f:
            f.write(self.log)

    def init(self, run_config: RunConfig):
        super().init(run_config)
        if self.answer_similarity is None and self.weights[1] != 0:
            self.answer_similarity = AnswerSimilarity(
                llm=self.llm, embeddings=self.embeddings
            )

    def _compute_statement_presence(self, prediction: t.Any) -> float:
        assert self.llm is not None, "LLM must be set"

        key_map = [
            "TP",
            "FP",
            "FN",
        ]
        if prediction:
            prediction = [prediction.get(k, np.nan) for k in key_map]
            tp, fp, fn = [
                len(item) if isinstance(item, list) else np.nan for item in prediction
            ]
            if any([np.isnan(i) for i in [tp, fp, fn]]):
                score = np.nan
            else:
                score = tp / (tp + 0.5 * (fp + fn)) if tp > 0 else 0
        else:
            score = np.nan

        return score

    async def _ascore(self, row: t.Dict, callbacks: Callbacks, is_async: bool) -> float:
        assert self.llm is not None, "LLM must be set"

        q, a, g = row["question"], row["answer"], row["ground_truth"]
        p_value = self.correctness_prompt.format(question=q, ground_truth=g, answer=a)
        is_statement_present = await self.llm.generate(
            p_value, callbacks=callbacks, is_async=is_async
        )

        prediction = await json_loader.safe_load(
            is_statement_present.generations[0][0].text, self.llm, is_async=is_async
        )
        f1_score = self._compute_statement_presence(prediction)

        self.log += (
            '\n\n-------------\n\n'
            f'Question: {q}\n'
            f'Answer: {a}\n'
            f'Truth: {g}\n'
            f'F1 Score: {f1_score}\n'
            f'Evaluator response: {prediction}\n'
        )

        if self.weights[1] == 0:
            similarity_score = 0
        else:
            assert self.answer_similarity is not None, "AnswerSimilarity must be set"

            similarity_score = await self.answer_similarity.ascore(
                row, callbacks=callbacks, is_async=is_async
            )

        score = np.average(
            [f1_score, similarity_score],
            weights=self.weights,
        )

        return float(score)

    def adapt(self, language: str, cache_dir: t.Optional[str] = None) -> None:
        assert self.llm is not None, "llm must be set to compute score"

        self.correctness_prompt = self.correctness_prompt.adapt(
            language, self.llm, cache_dir
        )

    def save(self, cache_dir: t.Optional[str] = None) -> None:
        self.correctness_prompt.save(cache_dir)


@dataclass
class BinaryAnswerCorrectness(MetricWithLLM, MetricWithEmbeddings):
    """
    """

    name: str = "binary_answer_correctness"  # type: ignore[reportIncompatibleMethodOverride]
    evaluation_mode: EvaluationMode = EvaluationMode.qga  # type: ignore[reportIncompatibleMethodOverride]
    correctness_prompt: Prompt = field(default_factory=lambda: BINARY_CORRECTNESS_PROMPT)

    def __post_init__(self: t.Self):
        self.log = ''

    def __del__(self):
        with open('metric_binary_answer_correctness_log.txt', 'w') as f:
            f.write(self.log)
        # pass

    def init(self, run_config: RunConfig):
        super().init(run_config)

    def _compute_statement_presence(self, prediction: t.Any) -> float:
        assert self.llm is not None, "LLM must be set"

        if 'true' in prediction.lower():
            score = 1.0
        elif 'false' in prediction.lower():
            return 0.0
        else:
            score = np.nan

        return score

    async def _ascore(self, row: t.Dict, callbacks: Callbacks, is_async: bool) -> float:
        assert self.llm is not None, "LLM must be set"

        q, a, g = row["question"], row["answer"], row["ground_truth"]
        p_value = self.correctness_prompt.format(question=q, truth=g, generated_answer=a)
        prediction = await self.llm.generate(
            p_value, callbacks=callbacks, is_async=is_async
        )
        # print('x', is_statement_present)

        # prediction = await json_loader.safe_load(
        #     is_statement_present.generations[0][0].text, self.llm, is_async=is_async
        # )
        prediction = prediction.generations[0][0].text
        score = self._compute_statement_presence(prediction)

        self.log += (
            '\n\n-------------\n\n'
            f'Question: {q}\n'
            f'Answer: {a}\n'
            f'Truth: {g}\n'
            f'Score: {score}\n'
            f'Evaluator response: {prediction}\n'
        )

        return float(score)

    def adapt(self, language: str, cache_dir: t.Optional[str] = None) -> None:
        assert self.llm is not None, "llm must be set to compute score"

        self.correctness_prompt = self.correctness_prompt.adapt(
            language, self.llm, cache_dir
        )

    def save(self, cache_dir: t.Optional[str] = None) -> None:
        self.correctness_prompt.save(cache_dir)



answer_correctness = AnswerCorrectness()
binary_answer_correctness = BinaryAnswerCorrectness()

# can't open a file in __del__, so...
from atexit import register

@register
def _atexit():
    global answer_correctness
    global binary_answer_correctness
    del answer_correctness
    del binary_answer_correctness