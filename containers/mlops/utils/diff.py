from typing import Tuple, Union

from pydantic import BaseModel

DiffLineType = Tuple[str, Tuple[str, ...], Union[str, None], Union[str, None]]


class DiffLine(BaseModel):
    action: str
    path: Tuple[str, ...]
    old_value: Union[str, None]
    new_value: Union[str, None]

    @staticmethod
    def from_tuple(diff_line: DiffLineType) -> "DiffLine":
        return DiffLine(
            action=diff_line[0],
            path=diff_line[1],
            old_value=diff_line[2],
            new_value=diff_line[3],
        )
