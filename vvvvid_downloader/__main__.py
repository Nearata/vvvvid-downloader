import logging
from pathlib import Path
from re import sub as re_sub
from shutil import move, rmtree
from subprocess import run as sp_run

from click import command, option
from httpx import Client
from inquirer import list_input
from rich.logging import RichHandler
from rich.progress import track
from rich.prompt import IntPrompt, Prompt

from vvvvid_downloader import __version__

from .vvvvid import ds

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],
)
log = logging.getLogger("vvvvid")


@command()
@option("--download", default=False, is_flag=True)
def main(download: bool) -> None:
    log.info(f"VVVVID Downloader {__version__}")

    if download:
        try:
            sp_run(["ffmpeg", "-loglevel", "quiet"])
        except Exception:
            log.critical("FFmpeg non trovato.")
            exit()

    show_id = IntPrompt.ask("ID Show")

    session = Client(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"
        },
        http2=True,
    )

    # Get connection ID
    response = session.get("https://www.vvvvid.it/user/login")
    conn_id = response.json()["data"]["conn_id"]

    # Get info about the show by its ID
    response = session.get(
        f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/info/?conn_id={conn_id}",
    )
    json = response.json()

    if json["result"] != "ok":
        message = json["message"]
        log.critical(message)
        exit()

    data = json["data"]
    title = data["title"]
    log.info(f"Scarico info su {title}...")

    video_format = data["video_format"]

    # Get the seasons of the show (this could also contain dubbed versions)
    response = session.get(
        f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/seasons/?conn_id={conn_id}",
    )
    json = response.json()
    data = json["data"]

    # Ask the user the season to download
    questions = [i["name"] for i in data]
    choice = list_input(f"Seleziona la versione che vuoi scaricare", choices=questions)

    # Get selected season data
    season_data = {}
    for i in data:
        if i["name"] == choice:
            season_data.update(i)

    episodes = season_data["episodes"]

    # Remove unplayable episodes
    for index, i in enumerate(episodes):
        if not i["playable"]:
            del episodes[index]

    for index, i in enumerate(episodes):
        season_id = i["season_id"]
        video_id = i["video_id"]
        response = session.get(
            f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/season/{season_id}?video_id={video_id}&conn_id={conn_id}",
        )
        json = response.json()

        for i2 in json["data"]:
            if video_id != i2["video_id"]:
                continue

            episodes[index]["show_title"] = i2["show_title"]
            episodes[index]["video_type"] = i2["video_type"]

            if "embed_info" in i2:
                episodes[index]["embed_info"] = i2["embed_info"]

            if "embed_info_sd" in i2:
                episodes[index]["embed_info_sd"] = i2["embed_info_sd"]

    qualities = {}
    questions = []
    if video_format == "SD":
        questions.append("SD")

        if "embed_info" in episodes[0]:
            qualities.update({"sd": "embed_info"})
        else:
            qualities.update({"sd": "embed_info_sd"})
    else:
        questions.append("HD")
        questions.append("SD")
        qualities.update({"hd": "embed_info", "sd": "embed_info_sd"})

    # Ask the user in which quality to download
    quality = list_input(f"Seleziona la qualità", choices=questions)

    # Get the embed_info code based on the answer of the user
    quality_code = qualities[quality.lower()]

    if len(episodes) > 1:
        choice = list_input(
            f"Sono disponibili {len(episodes)} episodi. Vuoi che li scarico tutti?",
            default="Si",
            choices=["Si", "No"],
        )
        if choice == "No":
            log.info(
                f"Inserisci gli episodi che vuoi scaricare separati da una virgola (,). Esempio: 1,4,5"
            )
            answer = None

            while not answer:
                p = Prompt.ask("Episodi", default=None)

                if not p:
                    continue

                answer = [int(i) for i in p.split(",")]

            episodes = [i for index, i in enumerate(episodes, 1) if index in answer]

    path = None

    for i in track(episodes, "Scarico..."):
        show_title = i["show_title"]
        episode_number = i["number"]

        path = Path().joinpath("vvvvid", show_title, "temp")
        path.mkdir(exist_ok=True, parents=True)

        url = ds(i[quality_code])

        video_type = i["video_type"]
        if video_type == "video/rcs":
            url = (
                url.replace("http:", "https:")
                .replace(".net/z", ".net/i")
                .replace("manifest.f4m", "master.m3u8")
            )
        else:
            url = url.replace(
                url,
                f"https://or01.top-ix.org/videomg/_definst_/mp4:{url}/playlist.m3u8",
            )

        output = re_sub(r"\s", "_", f"{show_title}_Ep_{episode_number}_{quality}")

        log.info(f"Scarico episodio #{episode_number}")

        response = session.get(url)

        if not download:
            playlist_path = Path().joinpath(path, f"{output}.m3u8")

            if not playlist_path.exists():
                with open(playlist_path, "wb") as dest_file:
                    for data in response.iter_bytes(32768):
                        dest_file.write(data)

                move(playlist_path, path.parent.joinpath(playlist_path.name))
            continue

        sp_run(
            [
                "ffmpeg",
                "-i",
                url,
                "-c",
                "copy",
                "-bsf:a",
                "aac_adtstoasc",
                str(Path().joinpath(path.parent, f"{output}.mp4").absolute()),
            ],
        )

    if path and path.exists():
        rmtree(path)

    session.close()
    print("Download completato.")


if __name__ == "__main__":
    main()
