"""Modele Pydantic folosite in achizitia datelor"""

from pydantic import BaseModel
from datetime import datetime
from typing import Set, Dict, Any, Literal


class TrackData(BaseModel):
    # id: int  # id intern
    spotifyId: str  # id spotify
    trackName: str  # nume
    genre: str  # gen
    artists: list[str]  # artisti
    release_date: datetime  # data lansare
    duration: int  # durata in ms
    popularity: int  # "popularitate"
    explicit: bool  # continut explicit
    # date extra Spotify

    # acustica: float
    # danceability: float
    # energie: float
    # instrumental: float
    # cheie: int
    # liveness: float
    # loudness: float
    # mode: int
    # speechiness: float
    # tempo: float
    # time_signature: int
    # valence: float

    # Modific metoda asta ca sa ii specific sa transforme data in text ISO
    def model_dump(
        self,
        *,
        mode: str = "python",
        include: Set[int] | Set[str] | Dict[int, Any] | Dict[str, Any] | None = None,
        exclude: Set[int] | Set[str] | Dict[int, Any] | Dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none"] | Literal["warn"] | Literal["error"] = True,
        serialize_as_any: bool = False
    ) -> dict[str, Any]:

        d = super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any,
        )

        d["release_date"] = self.release_date.isoformat()
        return d
