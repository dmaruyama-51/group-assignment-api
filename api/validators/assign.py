from fastapi import HTTPException


def validate_assignment_request(participants: int, rooms: int, rounds: int) -> None:
    """割り当てリクエストのバリデーション

    Args:
        participants (int): 参加者数
        rooms (int): 部屋数
        rounds (int): ラウンド数

    Raises:
        HTTPException: バリデーションエラー時
    """
    if participants < 1:
        raise HTTPException(
            status_code=400, detail="参加者数は1以上である必要があります"
        )
    if rooms < 1:
        raise HTTPException(status_code=400, detail="部屋数は1以上である必要があります")
    if rounds < 1:
        raise HTTPException(
            status_code=400, detail="ラウンド数は1以上である必要があります"
        )
    if participants < rooms:
        raise HTTPException(
            status_code=400, detail="参加者数は部屋数以上である必要があります"
        )
