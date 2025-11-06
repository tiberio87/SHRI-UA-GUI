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

## **Setup Automatico (Consigliato):**

### 📋 **Prerequisiti:**
Prima di iniziare, assicurati di avere installato:

1. **Git** - [Scarica da qui](https://git-scm.com/install/windows)
2. **Python 3.9+** - [Scarica da qui](https://www.python.org/downloads/)
3. **FFmpeg** - Installa da un terminale PowerShell con: `winget install ffmpeg`

### 🚀 **Installazione Rapida:**

1. **Scarica l'applicazione:**
   - Clona questa repository: `git clone https://github.com/tiberio87/SHRI-UA-GUI`
   - Oppure scarica lo ZIP dai [Releases](https://github.com/tiberio87/SHRI-UA-GUI/releases)

2. **Prepara il file API Keys:**
   - Crea un file `api_keys.json` nella stessa cartella dell'applicazione
   - Struttura minima richiesta:
   ```json
   {
     "tmdb_api": "la_tua_api_key_tmdb",
     "shri_api": "la_tua_api_key_shri",
     "imgbb_api": "",
     "discord_webhook": "",
     "qbit_url": "http://localhost",
     "qbit_port": "8080",
     "qbit_user": "",
     "qbit_pass": ""
   }
   ```

3. **Avvia l'applicazione:**
   - Esegui: `python "SHRI - Upload Assistant.py"`
   - Al primo avvio, clicca **"Setup da locale"**
   - L'applicazione farà tutto automaticamente:
     - ✅ Controlla le dipendenze di sistema
     - ✅ Verifica FFmpeg (con guida di installazione se mancante)
     - ✅ Scarica Upload-Assistant di Audionut
     - ✅ Crea l'ambiente virtuale
     - ✅ Installa tutte le dipendenze
     - ✅ Configura automaticamente i file

### 🔑 **Configurazione API Keys:**

**Dove ottenere le chiavi:**
- **TMDB API**: [Registrati su TMDB](https://www.themoviedb.org/settings/api)
- **SHRI API**: Fornita dal tracker
- **ImgBB API** (opzionale): [Registrati su ImgBB](https://api.imgbb.com/)

**Durante il setup automatico:**
- L'applicazione rileverà automaticamente le chiavi mancanti
- Ti mostrerà un dialog per compilare solo quelle obbligatorie
- Le chiavi opzionali possono essere configurate in seguito

### ⚙️ **Test della Configurazione:**

Dopo il setup, verifica che tutto funzioni:
- **🎬 Test FFmpeg**: Clicca il pulsante per verificare FFmpeg
- **🔄 Controlla aggiornamenti**: Testa la connessione a GitHub
- **📦 Installa req.**: Verifica l'ambiente virtuale

### 🔧 **Setup Manuale (Avanzato):**

### 🔧 **Setup Manuale (Avanzato):**

Se preferisci configurare tutto manualmente:

1. **Clona Upload-Assistant:**
   ```bash
   git clone https://github.com/Audionut/Upload-Assistant.git
   ```

2. **Crea ambiente virtuale:**
   ```bash
   cd Upload-Assistant
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Installa dipendenze:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura i file:**
   - Copia `data/example-config.py` in `data/config.py`
   - Modifica `config.py` con le tue API keys
   - Avvia la GUI e seleziona le cartelle manualmente

## **Aggiornamenti:**

### 🔄 **Aggiornamenti Automatici dalla GUI:**
- **"🔄 Controlla aggiornamenti Upload-Assistant"** - Aggiorna il bot tramite git pull
- **"📦 Installa req."** - Aggiorna le dipendenze Python
- **"🎬 Test FFmpeg"** - Verifica lo stato di FFmpeg

### 📥 **Aggiornamento della GUI:**
Per aggiornare questa GUI:
```bash
cd SHRI-UA-GUI
git pull origin main
```

## **Troubleshooting:**

### ❌ **Problemi Comuni:**

**"Git non trovato":**
- Installa Git da [git-scm.com](https://git-scm.com/install/windows)
- Riavvia l'applicazione dopo l'installazione

**"Python non trovato":**
- Installa Python 3.9+ da [python.org](https://www.python.org/downloads/)
- Durante l'installazione, spunta "Add Python to PATH"

**"FFmpeg non trovato":**
- Apri PowerShell e esegui: `winget install ffmpeg`
- Riavvia l'applicazione per verificare

**"API Keys mancanti":**
- L'applicazione ti guiderà nella configurazione
- Solo TMDB e SHRI API sono obbligatorie

**"Timeout durante il clone":**
- Verifica la connessione internet
- Prova a clonare manualmente: `git clone https://github.com/Audionut/Upload-Assistant.git`

### 🆘 **Supporto:**
- Controlla i [Issues](https://github.com/tiberio87/SHRI-UA-GUI/issues) per problemi noti
- Crea un nuovo issue per segnalare bug
- Il terminale integrato mostra log dettagliati per il debugging

## **Attribuzioni:**

<p>
  <a href="https://github.com/Audionut/Upload-Assistant"><img src="https://avatars.githubusercontent.com/u/13182387?s=48&v=4" alt="UA" height="20px;"></a>&nbsp;&nbsp;
</p>
