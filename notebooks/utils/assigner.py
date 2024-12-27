import random
from collections import defaultdict
from typing import List, Dict, Set, FrozenSet

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
    def __init__(self, total_participants: int, total_rooms: int, total_rounds: int) -> None:
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
    def __init__(self, total_participants: int, total_rooms: int, total_rounds: int) -> None:
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
                round_assignment[room].extend(self.participants[idx:idx + current_size])
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
    def __init__(self, total_participants: int, total_rooms: int, total_rounds: int) -> None:
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
        return sum(self.pair_history[frozenset((candidate, member))] for member in room_members)

    def _update_pair_history(self, candidate: int, room_members: List[int]) -> None:
        """ペア履歴を更新

        Args:
            candidate (int): 新規追加された参加者番号
            room_members (list): 既存の部屋メンバーリスト
        """
        for member in room_members:
            if member != candidate:
                self.pair_history[frozenset((candidate, member))] += 1

    def _select_next_candidate(self, available_candidates: List[int], room_members: List[int]) -> int:
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
            key=lambda x: self._calculate_pair_score(x, room_members)
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
                        participants_copy,
                        round_assignment[room]
                    )
                    
                    if candidate in participants_copy:
                        participants_copy.remove(candidate)

                    if candidate not in assigned:
                        round_assignment[room].append(candidate)
                        assigned.add(candidate)
                        self._update_pair_history(candidate, round_assignment[room])

            results.append(round_assignment)

        return results