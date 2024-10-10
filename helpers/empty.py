from pydantic import BaseModel


class Empty(BaseModel): ...


EMPTY = Empty()
