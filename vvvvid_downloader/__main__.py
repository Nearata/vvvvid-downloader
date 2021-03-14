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

    def __call__(self) -> None:
        user_agent, save_location, ffmpeg_location = self.__config()
        headers = {"User-Agent": user_agent}
        show_id = None

        Path(save_location).mkdir(exist_ok=True)

        while not show_id:
            try:
                show_id = int(input(f"{Fore.LIGHTYELLOW_EX}Show ID: {Fore.LIGHTWHITE_EX}"))

                if (show_id < 0):
                    print(f"{Fore.LIGHTRED_EX}[ERRORE] {Fore.LIGHTYELLOW_EX}Non può essere negativo.")
                    show_id = None

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

            # Get selected season data
            season_choice_data = {}
            for i in seasons_json["data"]:
                if i["name"] == seasons_choice:
                    season_choice_data.update(i)

            episodes = season_choice_data["episodes"]

            for idx, i in enumerate(episodes):
                if not i["playable"]:
                    del episodes[idx]

            # get season data each time we iterate over an episode
            for idx, i in enumerate(episodes):
                idata = s.get(f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/season/{i['season_id']}?video_id={i['video_id']}&conn_id={conn_id}", headers=headers)
                ijson = idata.json()

                for ii in ijson["data"]:
                    if i["video_id"] != ii["video_id"]:
                        continue

                    episodes[idx]["show_title"] = ii["show_title"]
                    episodes[idx]["video_type"] = ii["video_type"]

                    if "embed_info" in ii:
                        episodes[idx]["embed_info"] = ii["embed_info"]

                    if "embed_info_sd" in ii:
                        episodes[idx]["embed_info_sd"] = ii["embed_info_sd"]

            available_qualities = {}
            available_qualities_questions = []
            if video_format == "SD":
                available_qualities_questions.append("SD")

                if "embed_info" in episodes[0]:
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

            if len(episodes) > 1:
                choice = inquirer_list(f"{Fore.LIGHTYELLOW_EX}Sono disponibili {len(episodes)} episodi. Vuoi che li scarico tutti?{Fore.LIGHTWHITE_EX}", default="Si", choices=["Si", "No"])

                if choice == "No":
                    print(f"{Fore.LIGHTCYAN_EX}[ATTENZIONE] {Fore.RESET} Inserisci gli episodi che vuoi scaricare separati da una virgola (,). Esempio: 1,4,5")
                    answer = None

                    while not answer:
                        answer = input(f"{Fore.LIGHTYELLOW_EX}Episodi: {Fore.LIGHTWHITE_EX}")

                        if len(answer) == 0:
                            print("Devi inserire almeno 1 episodio.")
                            continue

                        answer = answer.split(",")
                        for i in answer:
                            try:
                                int(i)
                            except ValueError:
                                print(f"{Fore.LIGHTRED_EX}[ERRORE] {Fore.LIGHTYELLOW_EX}Devono essere solo numeri.")
                                answer = None
                                break

                        answer = [int(i) for i in answer]

                    episodes = [i for index, i in enumerate(episodes, 1) if index in answer]

            for i in episodes:
                url = ds(i[embed_info])

                if i["video_type"] == "video/rcs":
                    url = url.replace("http:", "https:").replace(".net/z", ".net/i").replace("manifest.f4m", "master.m3u8")
                elif i["video_type"] == "video/vvvvid":
                    url = url.replace(url, f"https://or01.top-ix.org/videomg/_definst_/mp4:{url}/playlist.m3u8")

                show_title = i["show_title"]
                episode_number = i["number"]
                output = sub(r"\s", "_", f"{show_title}_Ep_{episode_number}_{quality_choice}.mp4")

                print(f"{Fore.LIGHTGREEN_EX}[INFO] {Fore.LIGHTYELLOW_EX}Sto scaricando l'episodio numero: {Fore.LIGHTWHITE_EX}{episode_number}")

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

    def __config_create(self, path: Path) -> None:
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
