from itertools import combinations
from collections import defaultdict, Counter
from typing import Dict, List, FrozenSet, TypedDict, Counter as CounterType
import numpy as np


def calc_pair_frequencies(assignments: List[Dict[int, List[int]]]) -> Dict[FrozenSet[int], int]:
    """ペアの出現頻度を計算

    Args:
        assignments (List[Dict[int, List[int]]]): 全ラウンドの部屋割り当て結果
            各要素は {部屋番号: [参加者リスト]} の形式

    Returns:
        Dict[FrozenSet[int], int]: ペアの出現回数を示す辞書
            キー: 参加者2名のペア（FrozenSet）
            値: そのペアの出現回数
    """
    pair_frequencies: Dict[FrozenSet[int], int] = defaultdict(int)

    for round_assignment in assignments:
        for room, participants in round_assignment.items():
            for pair in combinations(participants, 2):  # 部屋内の全ペアを生成
                pair_frequencies[frozenset(pair)] += 1

    return pair_frequencies

def count_pair_frequency_distribution(pair_frequencies: Dict[FrozenSet[int], int]) -> CounterType[int]:
    """ペアの出現回数の分布を集計

    Args:
        pair_frequencies (Dict[FrozenSet[int], int]): ペアの出現頻度を示す辞書
            キー: 参加者2名のペア（FrozenSet）
            値: そのペアの出現回数

    Returns:
        Counter[int]: 出現回数ごとのペア数を示す辞書
            キー: ペアの出現回数
            値: その回数で出現したペアの数
    """
    return Counter(pair_frequencies.values())

def evaluate_pair_fairness(pair_frequencies: Dict[FrozenSet[int], int]) -> Dict[str, float]:
    """ペアの公平性を評価

    Args:
        pair_frequencies (Dict[FrozenSet[int], int]): ペアの出現頻度を示す辞書
            キー: 参加者2名のペア（FrozenSet）
            値: そのペアの出現回数

    Returns:
        Dict[str, float]: 評価指標を含む辞書
            mean: ペア出現回数の平均値
            std_dev: ペア出現回数の標準偏差
    """
    frequencies: List[int] = list(pair_frequencies.values())
    return {
        "mean": np.mean(frequencies),
        "std_dev": np.std(frequencies)
    }