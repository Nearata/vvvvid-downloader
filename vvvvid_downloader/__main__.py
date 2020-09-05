from configparser import ConfigParser
from sys import exit as exit_script
from pathlib import Path
from subprocess import run as sp_run
from re import sub

from requests import Session
from colorama import init as colorama_init
from colorama import Fore
from inquirer import list_input as inquirer_list

from vvvvid_downloader import ds


class Main():
    config_file = "config.ini"
    mappings = {
        "user-agent": {
            "title": "User Agent",
            "empty": "Inserisci un User Agent"
        },
        "save-location": {
            "title": "Save Location",
            "empty": "Inserisci il percorso dove salvare i file multimediali"
        },
        "ffmpeg-location": {
            "title": "FFmpeg Location",
            "empty": "Inserisci 'ffmpeg' se hai impostato una variabile d'ambiente, altrimenti inserisci il percorso diretto al file ffmpeg. (Per maggiori informazioni, visita 'https://github.com/nearata/vvvvid-downloader#Configurazione')"
        }
    }

    def __init__(self) -> None:
        colorama_init()

    def __call__(self):
        user_agent, save_location, ffmpeg_location = self.__config()
        headers = {"User-Agent": user_agent}
        show_id = None

        while not show_id:
            try:
                show_id = int(input(f"{Fore.LIGHTYELLOW_EX}Show ID: {Fore.LIGHTWHITE_EX}"))
            except ValueError:
                print(f"{Fore.LIGHTRED_EX}[ERRORE] {Fore.LIGHTYELLOW_EX}ID non valido.")

        with Session() as s:
            # Get connection ID
            login_response = s.get("https://www.vvvvid.it/user/login", headers=headers)
            conn_id = login_response.json()["data"]["conn_id"]

            # Get info about the show by its ID
            info_response = s.get(f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/info/?conn_id={conn_id}", headers=headers)
            info_json = info_response.json()

            # If the show ID does not exists, end the script
            if info_json["result"] != "ok":
                message = info_json["message"]
                exit_script(f"{Fore.LIGHTRED_EX}[Errore:] {Fore.LIGHTYELLOW_EX}{message}")

            title = info_json["data"]["title"]
            print(f"{Fore.LIGHTGREEN_EX}[INFO] {Fore.LIGHTYELLOW_EX + title}")

            video_format = info_json["data"]["video_format"]

            # Get the seasons of the show (this could also contain dubbed versions)
            seasons_response = s.get(f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/seasons/?conn_id={conn_id}", headers=headers)
            seasons_json = seasons_response.json()

            # Ask the user the season to download
            seasons_questions = [i["name"] for i in seasons_json["data"]]
            seasons_choice = inquirer_list(f"{Fore.LIGHTYELLOW_EX}Seleziona la versione che vuoi scaricare{Fore.LIGHTWHITE_EX}", choices=seasons_questions)

            # Get season_id and video_id from the first episode
            season_choice_data = [
                {
                    "season_id": i["episodes"][0]["season_id"],
                    "video_id": i["episodes"][0]["video_id"]
                } for i in seasons_json["data"] if i["name"] == seasons_choice
            ][0]
            season_id = season_choice_data["season_id"]
            video_id = season_choice_data["video_id"]

            # Get the episodes of the selected version
            season_choice_response = s.get(f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/season/{season_id}?video_id={video_id}&conn_id={conn_id}", headers=headers)
            season_choice_json = season_choice_response.json()

            available_qualities = {}
            available_qualities_questions = []
            if video_format == "SD":
                available_qualities_questions.append("SD")

                if "embed_info" in season_choice_json["data"][0]:
                    available_qualities.update({"sd": "embed_info"})
                else:
                    available_qualities.update({"sd": "embed_info_sd"})
            else:
                available_qualities_questions.append("HD")
                available_qualities_questions.append("SD")
                available_qualities.update({"hd": "embed_info", "sd": "embed_info_sd"})

            # Ask the user in which quality to download
            quality_choice = inquirer_list(f"{Fore.LIGHTYELLOW_EX}Seleziona la qualità{Fore.LIGHTWHITE_EX}", choices=available_qualities_questions)

            # Get the embed_info code based on the answer of the user
            embed_info = available_qualities[quality_choice.lower()]
            for i in season_choice_json["data"]:
                url = ds(i[embed_info])

                if i["video_type"] == "video/rcs":
                    url = url.replace("http:", "https:").replace(".net/z", ".net/i").replace("manifest.f4m", "master.m3u8")
                elif i["video_type"] == "video/vvvvid":
                    url = url.replace(url, f"https://or01.top-ix.org/videomg/_definst_/mp4:{url}/playlist.m3u8")

                show_title = i["show_title"]
                episode_number = i["number"]
                output = sub(r"\s", "_", f"{show_title}_Ep_{episode_number}_{quality_choice}.mp4")

                print(f"{Fore.LIGHTGREEN_EX}[INFO:] {Fore.LIGHTYELLOW_EX}Sto scaricando l'episodio numero: {Fore.LIGHTWHITE_EX}{episode_number}")

                # Download episode with FFmpeg, covert the file from .ts to .mp4 and save it
                sp_run([
                    "ffmpeg" if ffmpeg_location == "ffmpeg" else str(Path().joinpath(ffmpeg_location).absolute()),
                    "-loglevel",
                    "fatal",
                    "-i",
                    url,
                    "-c",
                    "copy",
                    "-bsf:a",
                    "aac_adtstoasc",
                    str(Path().joinpath(save_location, output).absolute())
                ])

        print(f"{Fore.LIGHTGREEN_EX}[INFO] {Fore.LIGHTYELLOW_EX}Download completato.")

    def __config(self) -> tuple:
        path = Path(__file__).parent.joinpath(self.config_file).absolute()

        if not path.exists():
            self.__config_create(path)

        config = ConfigParser()
        config.read(str(path))

        config_default = config["default"]

        for key in list(config_default.keys()):
            keymap = self.mappings[key]
            value = config_default[key]

            new_value = ""
            if value == "":
                new_value = self.__config_key_empty(keymap)
            else:
                new_value = self.__config_key_update(value, keymap)

            if new_value != "":
                config_default[key] = new_value
                with path.open("w") as f:
                    config.write(f)

        return tuple(config_default[key] for key in list(config_default.keys()))

    def __config_create(self, path: Path):
        config = ConfigParser()

        config["default"] = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
            "save-location": "",
            "ffmpeg-location": ""
        }

        with path.open("w") as f:
            config.write(f)

    def __config_key_empty(self, keymap: str) -> str:
        title = keymap["title"]
        print(f"{Fore.LIGHTGREEN_EX}[INFO] {Fore.LIGHTYELLOW_EX}{title} non può essere vuoto!")

        answer = None
        value_empty = keymap["empty"]

        while not answer:
            answer = input(f"{Fore.LIGHTYELLOW_EX}{value_empty}: {Fore.LIGHTWHITE_EX}")

            if len(answer) == 0:
                print("Non può essere vuoto")

        return answer

    def __config_key_update(self, value: str, keymap: str) -> str:
        title = keymap["title"]
        print(f"{Fore.LIGHTGREEN_EX}[INFO] {Fore.LIGHTYELLOW_EX}{title}: {Fore.LIGHTWHITE_EX}{value}")
        choice = inquirer_list(f"{Fore.LIGHTYELLOW_EX}Vuoi cambiare {title}?{Fore.LIGHTWHITE_EX}", default="No", choices=["Si", "No"])

        if choice == "Si":
            answer = None

            while not answer:
                answer = input(f"{Fore.LIGHTYELLOW_EX}Nuovo {title}: {Fore.LIGHTWHITE_EX}")

                if len(answer) == 0:
                    print("Non può essere vuoto")

            return answer

        return ""


if __name__ == "__main__":
    main = Main()
    main()
