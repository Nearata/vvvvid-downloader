# VVVVID Downloader

> Uno script in Python che permette di scaricare facilmente i video da VVVVID.

## Requisiti

- Python 3.8+
- Pipenv
- FFmpeg

## Installazione

1. Scarica [Python](https://www.python.org/) per il tuo sistema operativo e installalo.
2. Installa `Pipenv`. Es. `pip install pipenv`.
3. Clona questa repo oppure scarica il file ZIP.
4. Apri un terminale nella cartella ed esegui `pipenv install`.
5. Apri il file `config.ini` e modifica i campi seguendo le istruzioni scritte nella sezione `Configurazione` sotto.
6. Per scaricare un anime, apri il terminale nella cartella e scrivi `pipenv run python main.py` e segui le istruzioni a schermo. Per trovare l'ID, leggi la sezione `Come trovare l'ID di uno show` sotto.

## Come trovare l'ID di uno show

Apri VVVVID e clicca sullo show che vuoi scaricare:

Esempio: `https://www.vvvvid.it/show/1353/deca-dence` - 1353 è l'id dello show.

## Configurazione

Nel file di configurazione (`config.ini`) puoi modificare diversi campi:

- `user-agent`: L'user agent usato dallo script durante nelle richieste HTTP.
- `save-location`: La cartella dove lo script salverà i file (defualt `vvvvid`).
- `ffmpeg-location`: Deve puntare direttamente al file di ffmpeg, esempio: `/path/to/ffmpeg/bin/ffmpeg` (default `null`, quindi si aspetta ffmpeg disponibile globalmente nel sistema)

## License

Distributed under the MIT license. See `LICENSE` for more information.

## Contributing

1. Fork it
2. Commit your changes
3. Push to the branch
4. Create a new Pull Request
