from typing import Optional

from httpx import Client

from .responses import (
    InfoResponse,
    LoginResponse,
    SeasonObject,
    SeasonResponse,
    SeasonsObject,
    SeasonsResponse,
)


class Api:
    def __init__(self, client: Optional[Client] = None) -> None:
        """
        Creates an API instance.
        """

        self.client = client or Client(
            http2=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"
            },
        )
        self.conn_id: Optional[str] = None

    def login(self) -> LoginResponse:
        """
        Login to VVVVID.
        """

        r = self.client.get("https://www.vvvvid.it/user/login")
        login = LoginResponse(r)
        self.conn_id = login.conn_id
        return login

    def info(self, show_id: int) -> InfoResponse:
        """
        Get information about a show.
        """

        r = self.client.get(
            f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/info",
            params={"conn_id": self.conn_id},
        )
        return InfoResponse(r)

    def seasons(self, show_id: int) -> list[SeasonsObject]:
        """
        Get all the seasons the show has.
        """

        r = self.client.get(
            f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/seasons",
            params={"conn_id": self.conn_id},
        )
        s = SeasonsResponse(r)
        return s.get()

    def season(self, show_id: int, season_id: int) -> list[SeasonObject]:
        """
        Get information about a season.
        """

        r = self.client.get(
            f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/season/{season_id}",
            params={"conn_id": self.conn_id},
        )
        s = SeasonResponse(r)
        return s.get(self.client)
