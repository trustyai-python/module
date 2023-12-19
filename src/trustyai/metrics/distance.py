""""Distance metrics"""
# pylint: disable = import-error
from dataclasses import dataclass
from typing import List, Optional, Union, Callable

from org.kie.trustyai.metrics.language.distance import (
    Levenshtein as _Levenshtein,
    LevenshteinResult as _LevenshteinResult,
    LevenshteinCounters as _LevenshteinCounters,
)
from opennlp.tools.tokenize import Tokenizer
import numpy as np
import matplotlib.pyplot as plt
from trustyai import _default_initializer  # pylint: disable=unused-import


@dataclass
class LevenshteinCounters:
    """LevenshteinCounters Counters"""

    substitutions: int
    insertions: int
    deletions: int
    correct: int

    @staticmethod
    def convert(result: _LevenshteinCounters):
        """Converts a Java LevenshteinCounters to a Python LevenshteinCounters"""
        return LevenshteinCounters(
            substitutions=result.getSubstitutions(),
            insertions=result.getInsertions(),
            deletions=result.getDeletions(),
            correct=result.getCorrect(),
        )


@dataclass
class LevenshteinResult:
    """Levenshtein Result"""

    distance: float
    counters: LevenshteinCounters
    matrix: np.ndarray
    reference: List[str]
    hypothesis: List[str]

    @staticmethod
    def convert(result: _LevenshteinResult):
        """Converts a Java LevenshteinResult to a Python LevenshteinResult"""
        distance = result.getDistance()
        counters = LevenshteinCounters.convert(result.getCounters())
        data = result.getDistanceMatrix().getData()
        numpy_array = np.array(data)[1:, 1:]
        reference = result.getReferenceTokens()
        hypothesis = result.getHypothesisTokens()

        return LevenshteinResult(
            distance=distance,
            counters=counters,
            matrix=numpy_array,
            reference=reference,
            hypothesis=hypothesis,
        )

    def plot(self):
        """Plot the Levenshtein distance matrix"""
        cmap = plt.cm.viridis

        _, axes = plt.subplots()
        cax = axes.imshow(self.matrix, cmap=cmap, interpolation="nearest")

        plt.colorbar(cax)

        axes.set_xticks(np.arange(len(self.reference)))
        axes.set_yticks(np.arange(len(self.hypothesis)))
        axes.set_xticklabels(self.reference)
        axes.set_yticklabels(self.hypothesis)

        plt.setp(
            axes.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor"
        )

        nrows, ncols = self.matrix.shape
        for i in range(nrows):
            for j in range(ncols):
                color = (
                    "white" if self.matrix[i, j] < self.matrix.max() / 2 else "black"
                )
                axes.text(
                    j, i, int(self.matrix[i, j]), ha="center", va="center", color=color
                )

        plt.show()


def levenshtein(
    reference: str,
    hypothesis: str,
    tokenizer: Optional[Union[Tokenizer, Callable[[str], List[str]]]] = None,
) -> LevenshteinResult:
    """Calculate Levenshtein distance between two strings"""
    if not tokenizer:
        return LevenshteinResult.convert(
            _Levenshtein.calculateToken(reference, hypothesis)
        )
    if isinstance(tokenizer, Tokenizer):
        return LevenshteinResult.convert(
            _Levenshtein.calculateToken(reference, hypothesis, tokenizer)
        )
    if callable(tokenizer):
        tokenized_reference = tokenizer(reference)
        tokenized_hypothesis = tokenizer(hypothesis)
        return LevenshteinResult.convert(
            _Levenshtein.calculateToken(tokenized_reference, tokenized_hypothesis)
        )

    raise ValueError("Unsupported tokenizer")
