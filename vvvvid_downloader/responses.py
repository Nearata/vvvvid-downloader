from pathlib import Path
from typing import Any, Optional

from httpx import Client, Response

from .vvvvid import ds


class Base:
    def __init__(self, response: Response) -> None:
        self.response = response


class BaseObject:
    def __init__(self, data: dict[Any, Any]) -> None:
        self.data = data


class LoginResponse(Base):
    @property
    def conn_id(self) -> str:
        """
        Return a Connection ID used to authenticate the operations.
        """

        return self.response.json()["data"]["conn_id"]


class _WatchedByResponse(BaseObject):
    @property
    def id(self) -> int:
        return self.data["id"]

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def nick(self) -> str:
        return self.data["nick"]

    @property
    def thumbnail(self) -> str:
        return self.data["thumbnail"]


class InfoResponse(Base):
    @property
    def exists(self) -> bool:
        return "data" in self.response.json()

    @property
    def id(self) -> int:
        return self.response.json()["data"]["id"]

    @property
    def show_id(self) -> int:
        return self.response.json()["data"]["show_id"]

    @property
    def title(self) -> str:
        return self.response.json()["data"]["title"]

    @property
    def on_demand_type(self) -> int:
        return self.response.json()["data"]["ondemand_type"]

    @property
    def show_type(self) -> int:
        return self.response.json()["data"]["show_type"]

    @property
    def vod_mode(self) -> int:
        return self.response.json()["data"]["vod_mode"]

    @property
    def description(self) -> str:
        return self.response.json()["data"]["description"]

    @property
    def audio_format(self) -> str:
        return self.response.json()["data"]["audio_format"]

    @property
    def date_published(self) -> str:
        return self.response.json()["data"]["date_published"]

    @property
    def video_format(self) -> str:
        return self.response.json()["data"]["video_format"]

    @property
    def views(self) -> int:
        return self.response.json()["data"]["views"]

    @property
    def watched_by(self) -> list[_WatchedByResponse]:
        if "watched_by" not in self.response.json()["data"]:
            return []

        return [
            _WatchedByResponse(i) for i in self.response.json()["data"]["watched_by"]
        ]


class EpisodesObject(BaseObject):
    @property
    def id(self) -> int:
        return self.data["id"]

    @property
    def season_id(self) -> int:
        return self.data["season_id"]

    @property
    def video_id(self) -> int:
        return self.data["video_id"]

    @property
    def number(self) -> str:
        return self.data["number"]

    @property
    def title(self) -> str:
        return self.data["title"]

    @property
    def thumbnail(self) -> str:
        return self.data["thumbnail"]

    @property
    def description(self) -> str:
        return self.data["description"]

    @property
    def expired(self) -> bool:
        return self.data["expired"]

    @property
    def seen(self) -> bool:
        return self.data["seen"]

    @property
    def playable(self) -> bool:
        return self.data["playable"]

    @property
    def ondemand_type(self) -> int:
        return self.data["ondemand_type"]

    @property
    def is_added_to_watchlist(self) -> bool:
        return self.data["is_added_to_watchlist"]

    @property
    def vod_mode(self) -> int:
        return self.data["vod_mode"]


class SeasonsObject(BaseObject):
    @property
    def id(self) -> int:
        return self.data["season_id"]

    @property
    def show_id(self) -> int:
        return self.data["show_id"]

    @property
    def season_id(self) -> int:
        return self.data["season_id"]

    @property
    def show_type(self) -> int:
        return self.data["show_type"]

    @property
    def number(self) -> int:
        return self.data["number"]

    @property
    def episodes(self) -> list[EpisodesObject]:
        return [EpisodesObject(i) for i in self.data["episodes"]]

    @property
    def name(self) -> str:
        return self.data["name"]


class SeasonsResponse(Base):
    def get(self) -> list[SeasonsObject]:
        return [SeasonsObject(i) for i in self.response.json()["data"]]


class DownloadResponse:
    HTTP_FAILED: int = 0
    HTTP_SUCCESS: int = 1
    FILE_EXISTS: int = 2
    OUTPUT_HAS_SUFFIX: int = 3


class SeasonObject(BaseObject):
    def __init__(self, data: dict[Any, Any], client: Client) -> None:
        super().__init__(data)
        self.client = client

    @property
    def season_id(self) -> int:
        return self.data["season_id"]

    @property
    def number(self) -> str:
        return self.data["number"]

    @property
    def show_title(self) -> str:
        return self.data["show_title"]

    @property
    def seen(self) -> bool:
        return self.data["seen"]

    @property
    def season_number(self) -> int:
        return self.data["season_number"]

    @property
    def show_id(self) -> int:
        return self.data["season_id"]

    @property
    def show_type(self) -> int:
        return self.data["show_type"]

    @property
    def ondemand_type(self) -> int:
        return self.data["ondemand_type"]

    @property
    def id(self) -> int:
        return self.data["id"]

    @property
    def video_id(self) -> int:
        return self.data["video_type"]

    @property
    def title(self) -> str:
        return self.data["title"]

    @property
    def views(self) -> int:
        return self.data["views"]

    @property
    def length(self) -> int:
        return self.data["length"]

    @property
    def video_type(self) -> str:
        return self.data["video_type"]

    @property
    def vast_url(self) -> str:
        raise NotImplementedError()

    @property
    def vast_config(self) -> None:
        raise NotImplementedError()

    @property
    def sponsor_url(self) -> str:
        return self.data["sponsor_url"]

    @property
    def is_rated(self) -> bool:
        return self.data["is_rated"]

    @property
    def is_shared(self) -> bool:
        return self.data["is_shared"]

    @property
    def embed_info(self) -> Optional[str]:
        return self.data.get("embed_info")

    @property
    def thumbnail(self) -> str:
        return self.data["thumbnail"]

    @property
    def source_type(self) -> str:
        return self.data["source_type"]

    @property
    def embed_info_sd(self) -> Optional[str]:
        return self.data.get("embed_info_sd")

    @property
    def playable(self) -> bool:
        return self.data["playable"]

    @property
    def video_shares(self) -> int:
        return self.data["video_shares"]

    @property
    def video_likes(self) -> int:
        return self.data["video_likes"]

    @property
    def expired(self) -> bool:
        return self.data["expired"]

    @property
    def midroll_timings(self) -> str:
        return self.data["midroll_timings"]

    @property
    def vod_mode(self) -> int:
        return self.data["vod_mode"]

    def url(self, embed_code: str) -> str:
        url = ds(embed_code)

        if self.video_type == "video/rcs":
            url = (
                url.replace("http:", "https:")
                .replace(".net/z", ".net/i")
                .replace("manifest.f4m", "master.m3u8")
            )

        if self.video_type == "video/vvvvid":
            url = url.replace(
                url,
                f"https://or01.top-ix.org/videomg/_definst_/mp4:{url}/playlist.m3u8",
            )

        return url

    def download(self, embed_code: str, output_dir: Path, output_name: str) -> int:
        if output_dir.suffix:
            return DownloadResponse.OUTPUT_HAS_SUFFIX

        url = self.url(embed_code)
        r = self.client.get(url)

        if not r.is_success:
            return DownloadResponse.HTTP_FAILED

        output_dir.mkdir(exist_ok=True, parents=True)

        if self.video_type == "video/vvvvid":
            flt: list[str] = list(
                filter(lambda i: i.endswith(".m3u8"), r.text.split("\n"))
            )

            url = url.replace("playlist.m3u8", flt[0])

            r = self.client.get(url)

            with output_dir.joinpath(f"{output_name}.m3u8").open("w") as dest_file:
                for s in r.text.split("\n"):
                    if s.endswith(".ts"):
                        s = url.replace(flt[0], s)

                    dest_file.write(f"{s}\n")

        if self.video_type == "video/rcs":
            playlist_path = output_dir.joinpath(f"{output_name}.m3u8")

            if playlist_path.exists():
                return DownloadResponse.FILE_EXISTS

            with playlist_path.open("wb") as dest_file1:
                for data in r.iter_bytes(32768):
                    dest_file1.write(data)

        if self.video_type == "video/dash":
            playlist_path = output_dir.joinpath(f"{output_name}.m3u8")

            flt: list[str] = list(
                filter(lambda i: i.endswith(".m3u8"), r.text.split("\n"))
            )

            r = self.client.get(url)

            with output_dir.joinpath(f"{output_name}.m3u8").open("w") as dest_file:
                for s in r.text.split("\n"):
                    if s.endswith(".m3u8"):
                        s = url.replace(flt[0], s)

                    dest_file.write(f"{s}\n")

        return DownloadResponse.HTTP_SUCCESS


class SeasonResponse(Base):
    def get(self, client: Client) -> list[SeasonObject]:
        return [SeasonObject(i, client) for i in self.response.json()["data"]]
