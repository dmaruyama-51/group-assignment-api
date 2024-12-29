import random
from collections import defaultdict
import itertools
import pulp
from typing import List, Dict, Set, FrozenSet
from fastapi import HTTPException

random.seed(0)


class BaseAssigner:
    """グループ割り当ての基底クラス

    各ラウンドでの参加者の部屋割り当てを管理する基底クラス

    Args:
        total_participants (int): 参加者の総数
        total_rooms (int): 部屋の総数
        total_rounds (int): ラウンドの総数

    Attributes:
        participants (list): 参加者番号のリスト（1からtotal_participantsまで）
        room_size (int): 各部屋の基本サイズ（参加者総数を部屋数で割った値）
        remainder (int): 参加者を部屋に均等に分けた後の余り
    """

    def __init__(
        self, total_participants: int, total_rooms: int, total_rounds: int
    ) -> None:
        self.total_participants: int = total_participants
        self.total_rooms: int = total_rooms
        self.total_rounds: int = total_rounds
        self.participants: List[int] = list(range(1, total_participants + 1))
        self.room_size: int = total_participants // total_rooms
        self.remainder: int = total_participants % total_rooms

    def _get_room_size(self, room: int) -> int:
        """各部屋の参加者数を計算する

        Args:
            room (int): 部屋番号

        Returns:
            int: 指定された部屋の参加者数
        """
        return self.room_size + (1 if room <= self.remainder else 0)


class RandomAssigner(BaseAssigner):
    """ランダムな割り当て

    各ラウンドで参加者をランダムにシャッフルし、指定された部屋数に均等に振り分ける。

    Args:
        total_participants (int): 参加者の総数
        total_rooms (int): 部屋の総数
        total_rounds (int): ラウンドの総数
    """

    def __init__(
        self, total_participants: int, total_rooms: int, total_rounds: int
    ) -> None:
        super().__init__(total_participants, total_rooms, total_rounds)

    def generate_assignments(self) -> List[Dict[int, List[int]]]:
        """全ラウンドの部屋割り当てを生成

        各ラウンドで参加者をランダムにシャッフルし、部屋に振り分ける。

        Returns:
            list[defaultdict]: 各ラウンドの部屋割り当て結果
        """
        results: List[Dict[int, List[int]]] = []
        for _ in range(self.total_rounds):
            random.shuffle(self.participants)
            round_assignment: Dict[int, List[int]] = defaultdict(list)
            idx: int = 0

            for room in range(1, self.total_rooms + 1):
                current_size: int = self._get_room_size(room)
                round_assignment[room].extend(
                    self.participants[idx : idx + current_size]
                )
                idx += current_size

            results.append(round_assignment)
        return results


class GreedyAssigner(BaseAssigner):
    """Greedy法による割当

    過去のペア履歴を考慮し、同じペアができるだけ発生しないように各ラウンドでの割り当てを決定する。

    Args:
        total_participants (int): 参加者の総数
        total_rooms (int): 部屋の総数
        total_rounds (int): ラウンドの総数

    Attributes:
        pair_history (defaultdict): 参加者のペアとその発生回数を記録する辞書
    """

    def __init__(
        self, total_participants: int, total_rooms: int, total_rounds: int
    ) -> None:
        super().__init__(total_participants, total_rooms, total_rounds)
        self.pair_history: Dict[FrozenSet[int], int] = defaultdict(int)

    def _calculate_pair_score(self, candidate: int, room_members: List[int]) -> int:
        """候補者と既存メンバー間のペアスコアを計算

        Args:
            candidate (int): 候補者の参加者番号
            room_members (list): 既存の部屋メンバーリスト

        Returns:
            int: ペアの発生回数の合計
        """
        return sum(
            self.pair_history[frozenset((candidate, member))] for member in room_members
        )

    def _update_pair_history(self, candidate: int, room_members: List[int]) -> None:
        """ペア履歴を更新

        Args:
            candidate (int): 新規追加された参加者番号
            room_members (list): 既存の部屋メンバーリスト
        """
        for member in room_members:
            if member != candidate:
                self.pair_history[frozenset((candidate, member))] += 1

    def _select_next_candidate(
        self, available_candidates: List[int], room_members: List[int]
    ) -> int:
        """次の候補者を選択

        既存メンバーとのペア発生回数が最小となる候補者を選択する。

        Args:
            available_candidates (list): 割り当て可能な参加者リスト
            room_members (list): 既存の部屋メンバーリスト

        Returns:
            int: 選択された参加者番号
        """
        if not available_candidates:
            # 候補者がいない場合は、未割当の参加者からランダムに選択
            return random.choice(list(set(self.participants) - set(room_members)))

        # ペア履歴スコアが最小となる候補を選択
        return min(
            available_candidates,
            key=lambda x: self._calculate_pair_score(x, room_members),
        )

    def generate_assignments(self) -> List[Dict[int, List[int]]]:
        """全ラウンドの部屋割り当てを生成

        各ラウンドでペアの重複を最小限に抑えながら部屋割り当てを行う。

        Returns:
            list[defaultdict]: 各ラウンドの部屋割り当て結果
        """
        results: List[Dict[int, List[int]]] = []

        for _ in range(self.total_rounds):
            round_assignment: Dict[int, List[int]] = defaultdict(list)
            assigned: Set[int] = set()
            participants_copy: List[int] = self.participants[:]
            random.shuffle(participants_copy)

            for room in range(1, self.total_rooms + 1):
                current_size: int = self._get_room_size(room)

                while len(round_assignment[room]) < current_size:
                    candidate: int = self._select_next_candidate(
                        participants_copy, round_assignment[room]
                    )

                    if candidate in participants_copy:
                        participants_copy.remove(candidate)

                    if candidate not in assigned:
                        round_assignment[room].append(candidate)
                        assigned.add(candidate)
                        self._update_pair_history(candidate, round_assignment[room])

            results.append(round_assignment)

        return results


class OptimizationAssigner(BaseAssigner):
    """数理最適化による割り当て

    過去のペア履歴を考慮し、数理最適化を用いて各ラウンドでの割り当てを決定する。

    Args:
        total_participants (int): 参加者の総数
        total_rooms (int): 部屋の総数
        total_rounds (int): ラウンドの総数

    Attributes:
        history (set): 過去に発生したペアの集合
    """

    def __init__(
        self, total_participants: int, total_rooms: int, total_rounds: int
    ) -> None:
        super().__init__(total_participants, total_rooms, total_rounds)
        self.history: Set[tuple] = set()

    def _generate_random_assignment(self) -> Dict[int, List[int]]:
        """ランダムな割り当てを生成"""
        participants = self.participants[:]
        random.shuffle(participants)
        assignment = {
            j + 1: participants[j * self.room_size : (j + 1) * self.room_size]
            for j in range(self.total_rooms)
        }

        remainder = participants[self.total_rooms * self.room_size :]
        for i, participant in enumerate(remainder):
            assignment[(i % self.total_rooms) + 1].append(participant)
        return assignment

    def _optimize_round(self) -> Dict[int, List[int]]:
        """1ラウンド分の最適化

        Returns:
            Dict[int, List[int]]: 部屋割り当て結果

        Raises:
            HTTPException: 最適解が見つからない場合
        """
        rooms = list(range(self.total_rooms))

        problem = pulp.LpProblem("Optimize_Round", pulp.LpMinimize)

        # 変数定義
        x = {
            (i, j): pulp.LpVariable(f"x_{i}_{j}", 0, 1, pulp.LpBinary)
            for i in self.participants
            for j in rooms
        }
        y = {
            (i1, i2, j): pulp.LpVariable(f"y_{i1}_{i2}_{j}", 0, 1, pulp.LpBinary)
            for i1, i2 in itertools.combinations(self.participants, 2)
            for j in rooms
        }

        # 目的関数: 過去に割り当てられたペアの重複を最小化
        problem += pulp.lpSum(
            (1 if (i1, i2) in self.history else 0) * y[i1, i2, j]
            for i1, i2 in itertools.combinations(self.participants, 2)
            for j in rooms
        )

        # 制約 1: 各参加者は1つのルームに割り当てられる
        for i in self.participants:
            problem += pulp.lpSum(x[i, j] for j in rooms) == 1

        # 制約 2: 各ルームの人数は均等またはほぼ均等
        for j in rooms:
            problem += pulp.lpSum(x[i, j] for i in self.participants) >= self.room_size
            problem += (
                pulp.lpSum(x[i, j] for i in self.participants) <= self.room_size + 1
            )

        # 制約 3: 補助変数 y の定義
        for i1, i2 in itertools.combinations(self.participants, 2):
            for j in rooms:
                problem += y[i1, i2, j] <= x[i1, j]
                problem += y[i1, i2, j] <= x[i2, j]
                problem += y[i1, i2, j] >= x[i1, j] + x[i2, j] - 1

        problem.solve()

        if problem.status == pulp.LpStatusOptimal:
            return {
                j + 1: [i for i in self.participants if pulp.value(x[i, j]) == 1]
                for j in rooms
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="最適な部屋割り当てを見つけることができませんでした。条件を変更して再度お試しください。",
            )

    def generate_assignments(self) -> List[Dict[int, List[int]]]:
        """全ラウンドの部屋割り当てを生成

        Returns:
            List[Dict[int, List[int]]]: 各ラウンドの部屋割り当て結果
        """
        assignments = []

        # 第1ラウンド: ランダム割当
        first_round = self._generate_random_assignment()
        assignments.append(first_round)

        # 第1ラウンドのペアを記録
        for members in first_round.values():
            for i1, i2 in itertools.combinations(members, 2):
                self.history.add((i1, i2))

        # 第2ラウンド以降: 最適化
        for t in range(1, self.total_rounds):
            assignment = self._optimize_round()

            if assignment:
                assignments.append(assignment)
                for members in assignment.values():
                    for i1, i2 in itertools.combinations(members, 2):
                        self.history.add((i1, i2))
            else:
                print(f"Round {t+1} could not be optimized.")
                break

        return assignments
