# VVVVID Downloader

> Uno script in Python per scaricare da VVVVID.

## Requisiti

- [Python](https://python.org) 3.9+
- [FFmpeg](https://ffmpeg.org/) (Opzionale, solo se si vogliono scaricare e convertire i file in .mp4)

## Installazione

```bash
pip install vvvvid_downloader
```

## Utilizzo

```bash
python -m vvvvid_downloader
```

Seguire le istruzioni a schermo.

## Opzioni

- `--download`: Permette di scaricare e convertire i file in .mp4. (Richiede FFmpeg)

## Output

Lo script creerà una cartella di nome `vvvvid`, con al suo interno una cartella con il nome del film che avete scaricato.

- Se avete usato l'opzione `--download`, vi ritroverete i file convertiti nel formato `.mp4`.
- In caso contrario, vi ritroverete un file `.m3u8` che potrete aprire con VLC o simili per eseguirne lo streaming.

## Come trovare l'ID di un anime

```bash
https://www.vvvvid.it/show/1353/deca-dence
```

L'ID è `1353`.

## Unlicense

See [UNLICENSE](UNLICENSE) for details.
