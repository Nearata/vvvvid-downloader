from json import dumps, loads
from pathlib import Path
from subprocess import run as sp_run

import typer

from .logging import error

DEFAULT = {
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
    "saveLocation": "",
    "ffmpegLocation": "",
}


def create_config(configpath: Path) -> None:
    if not configpath.exists():
        _write_config(configpath, DEFAULT)

    config = _read_config(configpath)

    while True:
        newsave = typer.prompt("Inserisci il percorso dove salvare gli anime")
        newsave_path = Path(newsave).absolute()
        if not newsave_path.exists():
            error("Il percorso inserito non esiste!")
            continue

        config.update({"saveLocation": newsave})
        break

    while True:
        newffmpeg = typer.prompt("Inserisci il percorso dove si trova il file `ffmpeg`")
        newffmpeg_path = Path(newffmpeg).absolute()
        if not newffmpeg_path.exists():
            try:
                sp_run([str(newffmpeg), "-loglevel", "quiet"])
            except Exception as e:
                error(str(e))
                continue

        config.update({"ffmpegLocation": newffmpeg})
        break

    _write_config(configpath, config)


def get_config(configpath: Path) -> dict:
    return _read_config(configpath)


def _write_config(path: Path, data: dict) -> None:
    with path.open("w") as f:
        f.write(dumps(data))


def _read_config(path: Path) -> dict:
    with path.open() as f:
        config: dict = loads(f.read())

    return config
