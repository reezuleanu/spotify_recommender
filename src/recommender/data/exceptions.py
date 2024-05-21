"""Exceptii Custom"""


class TrackNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AlbumNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ExpiredAccessToken(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
