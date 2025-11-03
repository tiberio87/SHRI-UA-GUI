# SHRI-Upload-Assistant-GUI
Interfaccia grafica per Audionut Upload-Assistant, Uno strumento semplice per semplificare il lavoro di upload.

Questo progetto è una GUI basata sul lavoro originale di Audionut https://github.com/Audionut/Upload-Assistant
Un ringraziamento speciale a lui per aver creato questo progetto.

## Cosa può fare:
  - Genera e analizza MediaInfo/BDInfo.
  - Genera e carica screenshot. Tonemapping HDR se configurato.
  - Usa srrdb per correggere i nomi scena usati nei siti.
  - Può recuperare descrizioni da PTP/BLU/Aither/LST/OE/BHD (automaticamente su match del nome file o tramite argomento).
  - Può estrarre e riutilizzare screenshot già presenti nelle descrizioni per saltare la generazione e l'upload.
  - Ottiene identificatori TMDb/IMDb/MAL/TVDB/TVMAZE.
  - Converte la numerazione assoluta in stagioni/episodi per Anime. Supporto Non-Anime con credenziali TVDB.
  - Genera .torrent personalizzati senza cartelle/nfo inutili.
  - Può riutilizzare torrent esistenti invece di crearne di nuovi.
  - Può cercare automaticamente nei client qBitTorrent (versione 5+) torrent già esistenti.
  - Genera il nome corretto per l'upload usando Mediainfo/BDInfo e TMDb/IMDb conforme alle regole del sito.
  - Controlla se il rilascio è già presente sul sito.
  - Aggiunge al client con resume veloce, seed immediato (rtorrent/qbittorrent/deluge/watch folder).
  - TUTTO CON INPUT MINIMO!
  - Attualmente funziona con .mkv/.mp4/Blu-ray/DVD/HD-DVDs.

## Tracker supportati:

ShareIsland

## **Setup:**
   - **RICHIEDE ALMENO PYTHON 3.9 E PIP3**
   - Ottieni il codice sorgente:
      - Clona la repo sul tuo sistema `git clone https://github.com/tiberio87/SHRI-UA-GUI`
      - oppure scarica lo zip dalla pagina dei rilasci e crea/sovrascrivi una copia locale.
      - Modifica `api_keys.json` con i tuoi dati
      - Installa l'ambiente virtuale python `python -m venv .venv`
      - Attiva l'ambiente virtuale `.venv\Scripts\activate`
      - Installa i moduli python necessari `pip install -r requirements.txt`
   - Modifica (se necessario) `config.py` con i tuoi dati
      - La chiave tmdb_api si ottiene da https://www.themoviedb.org/settings/api
      - Le chiavi API degli host immagini si ottengono dai rispettivi siti

## **Aggiornamenti:**
  - Per aggiornare il BOT premi il pulsante verde "Controlla aggiornamenti BOT"
  - Per aggiornare i moduli premi il pulsante verde "Controlla aggiornamenti dipendenze"

## **Attribuzioni:**

<p>
  <a href="https://github.com/Audionut/Upload-Assistant"><img src="https://avatars.githubusercontent.com/u/13182387?s=48&v=4" alt="UA" height="40px;"></a>&nbsp;&nbsp;
</p>
