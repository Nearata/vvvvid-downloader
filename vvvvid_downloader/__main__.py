import logging
from pathlib import Path
from re import sub as re_sub
from shutil import which
from subprocess import run as sp_run

from click import command, option
from inquirer import list_input
from rich.logging import RichHandler
from rich.progress import track
from rich.prompt import IntPrompt, Prompt

from vvvvid_downloader import __version__

from .api import Api
from .responses import DownloadResponse, SeasonObject

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

    ffmpeg_path = which("ffmpeg")

    if download and not ffmpeg_path:
        log.critical("FFmpeg non trovato.")
        exit()

    show_id = IntPrompt.ask("ID Show")

    api = Api()
    api.login()

    info = api.info(show_id)

    if not info.exists:
        log.critical("Questo show non esiste.")
        exit()

    log.info(f"Scarico info su [bold]{info.title}[/]...")

    # Get the seasons of the show (this could also contain dubbed versions)
    seasons = api.seasons(show_id)

    # Ask the user the season to download
    questions = [i.name for i in seasons]
    choice = list_input("Seleziona la versione che vuoi scaricare", choices=questions)

    season_flt = list(filter(lambda i: i.name == choice, seasons))
    season = api.season(show_id, season_flt[0].season_id)

    qualities = {}
    questions = []
    if info.video_format.lower() == "sd":
        questions.append("SD")

        if season[0].embed_info:
            qualities.update({"sd": "embed_info"})
        else:
            qualities.update({"sd": "embed_info_sd"})
    else:
        questions.append("HD")
        questions.append("SD")
        qualities.update({"hd": "embed_info", "sd": "embed_info_sd"})

    quality = list_input(f"Seleziona la qualità", choices=questions)
    quality_code = qualities[quality.lower()]

    if len(season) > 1:
        choice = list_input(
            f"{len(season)} episodi disponibili. Li scarico tutti?",
            default="Si",
            choices=["Si", "No"],
        )

        if choice == "No":
            log.info(
                f"Inserisci gli episodi che vuoi scaricare separati da una virgola (,).\nEsempio: 1,4,5"
            )
            answer = None

            while not answer:
                p = Prompt.ask("Episodi", default=None)

                if not p:
                    continue

                answer = [int(i) for i in p.split(",")]

            season = [i for index, i in enumerate(season, 1) if index in answer]

    i: SeasonObject
    for i in track(season, "Scarico..."):
        show_title = i.show_title
        episode_number = i.number

        embed_code = getattr(i, quality_code, "")
        output_dir = Path().joinpath("vvvvid", show_title)
        output_name = re_sub(r"\s", "_", f"{show_title}_Ep_{episode_number}_{quality}")

        log.info(f"Scarico episodio #{episode_number}...")

        response = i.download(embed_code, output_dir, output_name)

        if response == DownloadResponse.HTTP_FAILED:
            log.critical(
                f"Impossibile scaricare [bold]{show_title} - #{episode_number} (ID: {show_id})[/]."
            )
            continue

        if not download:
            continue

        input_full = output_dir.joinpath(f"{output_name}.m3u8").absolute()
        output_mp4 = output_dir.joinpath(f"{output_name}.mp4").absolute()

        if output_mp4.exists():
            log.warning(f"L'episodio {episode_number} è già stato scaricato.")
            continue

        sp_run(
            [
                ffmpeg_path,  # type: ignore
                "-protocol_whitelist",
                "https,file,tls,tcp",
                "-i",
                input_full,
                "-c",
                "copy",
                "-bsf:a",
                "aac_adtstoasc",
                str(output_mp4),
            ],
        )

    log.info("Download completato.")


if __name__ == "__main__":
    main()
