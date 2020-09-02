from configparser import ConfigParser
from sys import exit as exit_script
from pathlib import Path
from subprocess import run as sp_run
from re import sub
from click import command, option
from requests import Session
from colorama import init, Fore, Style
from inquirer import List as inquirer_list
from inquirer import prompt as inquirer_prompt
from vvvvid_downloader import ds


@command()
@option("--show-id", prompt="Show ID", help="ID dello show.", type=int, required=True)
def main(show_id):
    config = ConfigParser()
    config.read("config.ini")

    config_default = config["default"]
    save_location = Path().joinpath(config_default["save-location"]).absolute()
    ffmpeg_location = config_default["ffmpeg-location"]

    print(f"{Fore.GREEN + Style.BRIGHT}INFO: {Fore.WHITE}Gli show verranno salvati in: {Fore.YELLOW}{save_location}{Fore.WHITE}.")

    save_location_questions = [inquirer_list("choice", f"{Fore.LIGHTGREEN_EX}Vuoi cambiare la cartella di destinazione?{Fore.LIGHTYELLOW_EX}", choices=["Si", "No"], default="No")]
    answers = inquirer_prompt(save_location_questions)

    if answers.get("choice") == "Si":
        exit_script(f"{Style.BRIGHT}OK. {Fore.WHITE}Per cambiarla, apri il file {Fore.RED}config.ini {Fore.WHITE}e modifica il campo {Fore.RED}save-location{Fore.WHITE}.")

    if not save_location.exists():
        save_location.mkdir()

    user_agent = config_default["user-agent"]
    headers = {"User-Agent": user_agent}

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
            exit_script(f"{Fore.RED + Style.BRIGHT}Errore: {Fore.RESET + Style.NORMAL}{message}")

        video_format = info_json["data"]["video_format"]

        # Get the seasons of the show (this could also contain dubbed versions)
        seasons_response = s.get(f"https://www.vvvvid.it/vvvvid/ondemand/{show_id}/seasons/?conn_id={conn_id}", headers=headers)
        seasons_json = seasons_response.json()

        # Ask the user the season to download
        seasons_list = [i["name"] for i in seasons_json["data"]]
        questions = [inquirer_list("choice", message=f"{Fore.GREEN + Style.BRIGHT}Seleziona la versione che vuoi scaricare{Fore.YELLOW}", choices=seasons_list)]
        answers = inquirer_prompt(questions)

        # Get season_id and video_id from the first episode
        season_choice_data = [
            {
                "season_id": i["episodes"][0]["season_id"],
                "video_id": i["episodes"][0]["video_id"]
            } for i in seasons_json["data"] if i["name"] == answers.get("choice")
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
        quality_questions = [inquirer_list("choice", message=f"{Fore.GREEN + Style.BRIGHT}Seleziona la qualità{Fore.YELLOW}", choices=available_qualities_questions)]
        quality_answers = inquirer_prompt(quality_questions)
        quality_choice = quality_answers.get("choice")

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

            print(f"{Fore.GREEN + Style.BRIGHT}{Fore.WHITE}Sto scaricando l'episodio numero: {Fore.YELLOW}{episode_number}")

            # Download episode with FFmpeg, covert the file from .ts to .mp4 and save it
            sp_run([
                "ffmpeg" if ffmpeg_location == "null" else str(Path().joinpath(ffmpeg_location).absolute()),
                "-loglevel",
                "fatal",
                "-i",
                url,
                "-c",
                "copy",
                "-bsf:a",
                "aac_adtstoasc",
                str(save_location.joinpath(output).absolute())
            ])


if __name__ == "__main__":
    init()
    main()
