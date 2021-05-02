# VVVVID Downloader

> Uno script in Python per scaricare, in modo semplice, gli anime anime da VVVVID.

## Requisiti

- [Python](https://python.org) 3.9+
- [FFmpeg](https://ffmpeg.org/)

## Installazione

```bash
pip install vvvvid_downloader
```

## Utilizzo

```bash
python -m vvvvid_downloader
```

Segui le istruzioni a schermo. Per maggiori informazioni sui campi di configurazione, leggi la sezione [Configurazione](#Configurazione).

## Come trovare l'ID di un anime

Apri l'anime che vuoi scaricare da [VVVVID](https://www.vvvvid.it). Esempio:

```sh
https://www.vvvvid.it/show/1353/deca-dence
```

In questo caso, l'ID dell'anime è `1353`

## Configurazione

Al primo avvio dello script, vi verrà chiesto di completare due campi.

1. Dove salvare gli anime.
2. Il percorso che porta al file `ffmpeg`. (Se avete una variabile d'ambiente, inserite `ffmpeg`)

Se vorrete modificare in futuro questi campi, eseguite:

```bash
python -m vvvvid_downloader --edit-config
```

## Contributing

1. Fork it
2. Commit your changes
3. Push to the branch
4. Create a new Pull Request

## License

Distributed under the MIT license. See [LICENSE](LICENSE) for details.
