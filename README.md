# SHRI-Upload-Assistant-GUI
Interfaccia grafica per Audionut Upload-Assistant, Uno strumento semplice per semplificare il lavoro di upload.

Questo progetto è una GUI basata sul lavoro originale di Audionut https://github.com/Audionut/Upload-Assistant
Un ringraziamento speciale a lui per aver creato questo progetto.

## Cosa può fare la GUI:

### 🖥️ **Interfaccia Grafica Intuitiva:**
  - **Interfaccia user-friendly** con layout responsive per tutti i tipi di schermo
  - **Selezione file/cartelle** tramite dialog grafici (niente linea di comando!)
  - **Campi compilabili** per IMDb ID, TMDb ID, TAG gruppo, piattaforma streaming, edizione
  - **Combobox intelligenti** per tipo rilascio (Film MKV/Disco, Serie Episodio/Stagione)
  - **Checkbox seed automatico** per configurare il seeding post-upload
  - **Tooltip informativi** su ogni elemento per guidare l'utente

### 🔧 **Setup e Configurazione Automatica:**
  - **Setup completamente automatico** con un solo click
  - **Controllo dipendenze** automatico (Git, Python, pip, FFmpeg)
  - **Download automatico** di Upload-Assistant se non presente
  - **Creazione ambiente virtuale** automatica
  - **Installazione dipendenze** automatica con progress feedback
  - **Configurazione API keys** tramite dialog guidato
  - **Verifica FFmpeg** con guida di installazione Winget integrata

### 💻 **Terminale Integrato:**
  - **PowerShell integrato** direttamente nell'interfaccia
  - **Esecuzione comandi** in tempo reale con output colorato
  - **Controlli avanzati**: INVIO, Interrompi (Ctrl+C), Reset completo
  - **Cronologia comandi** e auto-scroll intelligente
  - **Gestione processi** con indicatori di stato visivi
  - **Font ingranditi** e output ottimizzato per la lettura

### 🚀 **Funzionalità Avanzate:**
  - **Aggiornamenti automatici** di Upload-Assistant tramite git pull
  - **Test integrati** per verificare FFmpeg e configurazioni
  - **Gestione errori robusta** con timeout e fallback automatici
  - **Salvataggio preferenze** per geometria finestra e modalità compatta
  - **Supporto finestre multiple** con ridimensionamento dinamico
  - **Modalità compatta** per schermi piccoli

### 📦 **Gestione Upload Semplificata:**
  - **Un click per l'upload** - tutti i parametri vengono passati automaticamente
  - **Validazione input** con controlli pre-upload
  - **Feedback visivo** durante tutte le operazioni
  - **Gestione tracker** ottimizzata per ShareIsland (SHRI)
  - **Configurazione rapida** di parametri avanzati senza editing manuale

### 🔄 **Manutenzione e Aggiornamenti:**
  - **Pulsanti dedicati** per aggiornare bot e dipendenze
  - **Editor config.py integrato** (Notepad++ o Notepad)
  - **Controllo stato sistema** con diagnostica integrata
  - **Backup automatico** delle configurazioni
  - **Log dettagliati** nel terminale per troubleshooting

### ✨ **Tutto il Potere di Upload-Assistant, Zero Complessità:**
Mantiene tutte le funzionalità avanzate del bot originale:
  - Generazione e analisi MediaInfo/BDInfo
  - Screenshot automatici con tonemapping HDR
  - Correzione nomi scena via srrdb
  - Recupero descrizioni da tracker esistenti
  - Gestione identificatori TMDb/IMDb/MAL/TVDB/TVMAZE
  - Creazione .torrent ottimizzati
  - Integrazione qBitTorrent automatica
  - **TUTTO CON INTERFACCIA GRAFICA - ZERO LINEA DI COMANDO!**

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

2. **Installa la dipendenza GUI:**
   - Apri PowerShell o Prompt dei Comandi
   - Esegui: `pip install customtkinter pywinpty`
   - Queste sono le uniche dipendenze necessarie per avviare la GUI

3. **Prepara il file API Keys:**
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

4. **Avvia l'applicazione:**
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

**"La GUI si blocca":**
- Premere il tasto giallo RESET GUI

### 🆘 **Supporto:**
- Controlla i [Issues](https://github.com/tiberio87/SHRI-UA-GUI/issues) per problemi noti
- Crea un nuovo issue per segnalare bug
- Il terminale integrato mostra log dettagliati per il debugging

## **Attribuzioni:**

<p>
  <a href="https://github.com/Audionut/Upload-Assistant"><img src="https://avatars.githubusercontent.com/u/13182387?s=48&v=4" alt="UA" height="30px;"></a>&nbsp;&nbsp;
</p>
