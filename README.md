# VVVVID Downloader

> Uno script in Python che permette di scaricare facilmente i video da VVVVID.

## Requisiti

- [Python](https://python.org) 3.8+
- [FFmpeg](https://ffmpeg.org/)

## Installazione

```sh
pip install vvvvid-downloader
```

## Utilizzo

```sh
python -m vvvvid_downloader
```

Segui le istruzioni a schermo. Per maggiori informazioni sui campi di configurazione, leggi la sezione `Configurazione` sotto.

## Come trovare l'ID di uno show

Apri uno show che vuoi scaricare da [VVVVID](https://www.vvvvid.it). Esempio:

```sh
https://www.vvvvid.it/show/1353/deca-dence
```

In questo caso, l'ID dello show è `1353`

## Configurazione

Al primo avvio dello script, vi verrà chiesto di completare i campi `save-location` e `ffmpeg-location`.

Ad ogni avvio, invece, vi verrà chiesto se volete o meno modificare il valore di ogni singolo campo.

- `user-agent`: Questo sarà l'User Agent che lo script userà per le richieste HTTP.
  - Esempio: `Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0`.
- `save-location`: Questo è il percorso alla cartella dove verranno salvati i file che lo script scaricherà.
  - Esempio: `C:\Utenti\<nome_utente>\Desktop\vvvvid`.
- `ffmpeg-location`: Questo è il percorso che deve portare al file `ffmpeg`.
  - Se avete impostato una variabile d'ambiente, potete anche inserire il nome della variabile.

## License

Distributed under the MIT license. See [LICENSE](LICENSE) for more information.

## Contributing

1. Fork it
2. Commit your changes
3. Push to the branch
4. Create a new Pull Request
