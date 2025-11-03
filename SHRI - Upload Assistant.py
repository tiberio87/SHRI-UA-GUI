import os
import subprocess
import shutil
import json
import re
import time
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import sys

# === Funzioni Helper per Gestione File ===
def get_resource_path(relative_path):
    """Ottiene il percorso corretto sia per script che per EXE"""
    try:
        # PyInstaller crea una cartella temp e memorizza il percorso in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Modalità development - usa la directory corrente
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def find_or_select_api_keys():
    """Trova il file api_keys.json o permette di selezionarlo"""
    # Prima prova nella directory corrente
    possible_paths = [
        "api_keys.json",  # Directory corrente
        get_resource_path("api_keys.json"),  # Nel bundle EXE
        os.path.join(os.path.dirname(sys.executable), "api_keys.json"),  # Accanto all'EXE
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_keys.json")  # Accanto al .py
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # Se non trovato, chiedi all'utente di selezionarlo
    messagebox.showinfo(
        "File api_keys.json non trovato", 
        "Il file api_keys.json non è stato trovato.\n\n"
        "Seleziona il file api_keys.json dalla finestra di dialogo che si aprirà."
    )

    selected_file = filedialog.askopenfilename(
        title="Seleziona il file api_keys.json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        initialdir=os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "."
    )

    if not selected_file:
        return None

    # Verifica che sia un file api_keys valido
    try:
        with open(selected_file, 'r', encoding='utf-8') as f:
            keys = json.load(f)
        # Verifica che contenga almeno alcune chiavi previste
        expected_keys = ['tmdb_api', 'imgbb_api', 'discord_webhook']
        if not any(key in keys for key in expected_keys):
            messagebox.showerror(
                "File non valido", 
                "Il file selezionato non sembra essere un file api_keys.json valido."
            )
            return None
        return selected_file
    except Exception as e:
        messagebox.showerror(
            "Errore lettura file", 
            f"Errore nel leggere il file selezionato:\n{e}"
        )
        return None

def validate_and_fill_api_keys(keys_file):
    """Valida le API keys e permette di compilare quelle mancanti"""
    try:
        with open(keys_file, "r", encoding="utf-8") as f:
            keys = json.load(f)
        
        # Campi obbligatori che devono essere sempre presenti
        required_fields = {"tmdb_api", "shri_api"}
        
        # Controlla se ci sono valori vuoti nei campi obbligatori
        missing_required = [key for key in required_fields if not keys.get(key, "").strip()]
        
        # Controlla anche se ci sono altri campi vuoti (per mostrarli nel popup)
        all_empty_keys = [key for key, value in keys.items() if not value or value.strip() == ""]
        
        if missing_required or all_empty_keys:
            # Mostra popup per compilare i valori mancanti
            result = show_api_keys_dialog(keys, all_empty_keys)
            if result:
                # Salva i nuovi valori
                with open(keys_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                return result
            else:
                return None  # Utente ha annullato
        
        return keys  # Tutto già compilato
    
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante la validazione di api_keys.json:\n{e}")
        return None

def show_api_keys_dialog(current_keys, empty_keys):
    """Mostra una finestra di dialogo per compilare le API keys mancanti"""
    
    dialog = ctk.CTkToplevel()
    dialog.title("🔑 Configurazione API Keys")
    dialog.geometry("550x700")
    dialog.resizable(False, False)
    dialog.transient()
    dialog.grab_set()  # Rende la finestra modale
    
    # Centra la finestra
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
    y = (dialog.winfo_screenheight() // 2) - (700 // 2)
    dialog.geometry(f"550x700+{x}+{y}")
    
    # Variabile per il risultato
    result = [None]
    
    # Titolo
    title_label = ctk.CTkLabel(
        dialog,
        text="🔑 CONFIGURAZIONE API KEYS",
        font=ctk.CTkFont(size=20, weight="bold")
    )
    title_label.pack(pady=20)
    
    info_label = ctk.CTkLabel(
        dialog,
        text="COMPILA I CAMPI OBBLIGATORI PER CONTINUARE.\nI CAMPI FACOLTATIVI POSSONO ESSERE LASCIATI VUOTI.",
        font=ctk.CTkFont(size=12)
    )
    info_label.pack(pady=(0, 20))
    
    # Frame scrollabile per i campi
    scroll_frame = ctk.CTkScrollableFrame(dialog, width=500, height=400)
    scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    # Dizionario per tenere traccia degli entry widgets
    entry_widgets = {}
    
    # Campi obbligatori e facoltativi
    required_fields = {"tmdb_api", "shri_api"}
    optional_fields = {"imgbb_api", "discord_webhook", "qbit_url", "qbit_port", "qbit_user", "qbit_pass"}
    
    # Descrizioni per ogni campo
    field_descriptions = {
        "tmdb_api": "TMDB API Key (per informazioni film/serie)",
        "imgbb_api": "ImgBB API Key (per upload immagini)",
        "shri_api": "SHRI API Key (per tracker)",
        "discord_webhook": "Discord Webhook URL (per notifiche)",
        "qbit_url": "qBittorrent URL (es: http://localhost)",
        "qbit_port": "qBittorrent Port (es: 8080)",
        "qbit_user": "qBittorrent Username",
        "qbit_pass": "qBittorrent Password"
    }
    
    # ====== SEZIONE CAMPI OBBLIGATORI ======
    required_section = ctk.CTkLabel(
        scroll_frame, 
        text="📋 CAMPI OBBLIGATORI", 
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="#ff6b6b"
    )
    required_section.pack(anchor="w", padx=10, pady=(10, 5))
    
    required_info = ctk.CTkLabel(
        scroll_frame,
        text="QUESTI CAMPI DEVONO ESSERE COMPILATI PER UTILIZZARE L'APPLICAZIONE:",
        font=ctk.CTkFont(size=10),
        text_color="gray"
    )
    required_info.pack(anchor="w", padx=10, pady=(0, 10))
    
    # Crea i campi obbligatori
    for key, value in current_keys.items():
        if key in required_fields:
            # Frame per ogni campo
            field_frame = ctk.CTkFrame(scroll_frame, fg_color="#2d1b2e")  # Colore leggermente diverso per evidenziare
            field_frame.pack(fill="x", padx=10, pady=5)
            
            # Nome del campo e descrizione
            label_text = f"🔴 {key} *OBBLIGATORIO*"
            if key in field_descriptions:
                label_text += f"\n{field_descriptions[key]}"
            
            label = ctk.CTkLabel(
                field_frame,
                text=label_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w",
                text_color="#ff6b6b"
            )
            label.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Campo di input
            entry = ctk.CTkEntry(
                field_frame,
                width=450,
                placeholder_text=f"Inserisci {key}...",
                border_color="#ff6b6b",
                border_width=2
            )
            entry.pack(padx=10, pady=(0, 10))
            entry.insert(0, value)
            
            entry_widgets[key] = entry
    
    # ====== SEZIONE CAMPI FACOLTATIVI ======
    optional_section = ctk.CTkLabel(
        scroll_frame, 
        text="⚙️ CAMPI FACOLTATIVI", 
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="#4a9eff"
    )
    optional_section.pack(anchor="w", padx=10, pady=(20, 5))
    
    optional_info = ctk.CTkLabel(
        scroll_frame,
        text="QUESTI CAMPI SONO OPZIONALI E POSSONO ESSERE CONFIGURATI SUCCESSIVAMENTE:",
        font=ctk.CTkFont(size=10),
        text_color="gray"
    )
    optional_info.pack(anchor="w", padx=10, pady=(0, 10))
    
    # Crea i campi facoltativi
    for key, value in current_keys.items():
        if key in optional_fields:
            # Frame per ogni campo
            field_frame = ctk.CTkFrame(scroll_frame)
            field_frame.pack(fill="x", padx=10, pady=5)
            
            # Nome del campo e descrizione
            label_text = f"🔵 {key} (facoltativo)"
            if key in field_descriptions:
                label_text += f"\n{field_descriptions[key]}"
            
            label = ctk.CTkLabel(
                field_frame, 
                text=label_text,
                font=ctk.CTkFont(size=11),
                anchor="w",
                text_color="#4a9eff"
            )
            label.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Campo di input
            entry = ctk.CTkEntry(
                field_frame,
                width=450,
                placeholder_text=f"Inserisci {key}... (opzionale)"
            )
            entry.pack(padx=10, pady=(0, 10))
            entry.insert(0, value)
            
            entry_widgets[key] = entry
    
    # Frame per i pulsanti
    button_frame = ctk.CTkFrame(dialog)
    button_frame.pack(pady=20, padx=20, fill="x")
    
    def save_keys():
        # Raccoglie tutti i valori
        new_keys = {}
        for key, entry in entry_widgets.items():
            new_keys[key] = entry.get().strip()
        
        # Controlla solo i campi obbligatori
        missing_required = []
        for field in required_fields:
            if field in new_keys and not new_keys[field]:
                missing_required.append(field)
        
        if missing_required:
            messagebox.showwarning(
                "Campi obbligatori mancanti",
                f"I seguenti campi obbligatori devono essere compilati:\n\n"
                f"• {chr(10).join(f'🔴 {field}' for field in missing_required)}\n\n"
                "Compila tutti i campi obbligatori per continuare."
            )
            return
        
        result[0] = new_keys
        dialog.destroy()
    
    def cancel():
        dialog.destroy()
    
    # Pulsanti
    cancel_btn = ctk.CTkButton(
        button_frame,
        text="❌ Annulla",
        command=cancel,
        fg_color="gray",
        hover_color="darkgray",
        width=120
    )
    cancel_btn.pack(side="left", padx=10)
    
    save_btn = ctk.CTkButton(
        button_frame,
        text="💾 Salva e Continua",
        command=save_keys,
        width=150,
        fg_color="#28a745",
        hover_color="#1e7a3a"
    )
    save_btn.pack(side="right", padx=10)
    
    # Aspetta che la finestra venga chiusa
    dialog.wait_window()
    
    return result[0]

def find_config_file():
    """Trova il file config.txt usando la stessa logica di api_keys.json"""
    possible_paths = [
        "config.txt",  # Directory corrente
        get_resource_path("config.txt"),  # Nel bundle EXE
        os.path.join(os.path.dirname(sys.executable), "config.txt"),  # Accanto all'EXE
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.txt")  # Accanto al .py
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # Se non trovato, crea un config.txt vuoto nella directory dell'EXE o script
    if getattr(sys, 'frozen', False):
        # Siamo in un EXE
        default_path = os.path.join(os.path.dirname(sys.executable), "config.txt")
    else:
        # Siamo in modalità development
        default_path = "config.txt"

    # Crea un file config.txt vuoto
    try:
        with open(default_path, 'w', encoding='utf-8') as f:
            f.write("# File di configurazione generato automaticamente\n")
        return default_path
    except:
        return "config.txt"  # Fallback

# === Tooltip ===
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 30
        y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left", background="#333333", foreground="white", relief="solid", borderwidth=1, font=("Arial", 12))
        label.pack(ipadx=6, ipady=3)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# === Terminale Integrato ===
class IntegratedTerminal:
    def __init__(self, parent):
        self.parent = parent
        self.process = None
        self.output_queue = queue.Queue()
        self.current_child_process = None  # Riferimento al processo figlio corrente

        # Frame per il terminale
        self.terminal_frame = ctk.CTkFrame(parent)

        # Etichetta del terminale
        self.terminal_label = ctk.CTkLabel(self.terminal_frame, text="🖥️ Terminale", font=("Arial", 16, "bold"))
        self.terminal_label.pack(pady=(10, 5))

        # Area di output del terminale con font più grande
        self.terminal_output = scrolledtext.ScrolledText(
            self.terminal_frame,
            height=15,
            width=80,
            bg="#1a1a1a",
            fg="#00ff00",
            font=("Consolas", 12),  # Font più grande (era 10)
            wrap=tk.WORD,
            state=tk.DISABLED,
            padx=5,  # Padding orizzontale
            pady=5   # Padding verticale per evitare che l'ultima linea sia troppo in basso
        )
        self.terminal_output.pack(padx=10, pady=(0, 5), fill="both", expand=True)

        # Frame per input e controlli
        self.control_frame = ctk.CTkFrame(self.terminal_frame)
        self.control_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Prima riga: Entry + pulsante INVIO
        self.input_frame = ctk.CTkFrame(self.control_frame)
        self.input_frame.pack(fill="x", pady=(5, 5))

        # Entry per input comandi con font più grande
        self.command_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Esegui un comando",
            font=("Consolas", 14)  # Font più grande (era 12)
        )
        self.command_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
        self.command_entry.bind("<Return>", self.execute_command)

        # Bottone INVIO
        self.execute_btn = ctk.CTkButton(
            self.input_frame,
            text="INVIO",
            command=self.execute_command,
            width=80,
            font=("Consolas", 12, "bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.execute_btn.pack(side="right", padx=(0, 5))

        # Seconda riga: Pulsanti di controllo
        self.buttons_frame = ctk.CTkFrame(self.control_frame)
        self.buttons_frame.pack(fill="x", pady=(0, 5))

        # Indicatore di stato del processo (a sinistra)
        self.status_label = ctk.CTkLabel(
            self.buttons_frame,
            text="💤 Pronto",
            font=("Consolas", 10),
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=(10, 5))

        # Bottone per pulire il terminale
        self.clear_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Pulisci Terminale",
            command=self.clear_terminal,
            width=120,
            fg_color="gray",
            hover_color="darkgray",
            font=("Consolas", 12)
        )
        self.clear_btn.pack(side="right", padx=(5, 5))

        # Bottone per interrompere il processo corrente (Ctrl+C)
        self.interrupt_btn = ctk.CTkButton(
            self.buttons_frame,
            text="INTERROMPI",
            command=self.interrupt_process,
            width=120,
            fg_color="red",
            hover_color="darkred",
            font=("Consolas", 12, "bold")
        )
        self.interrupt_btn.pack(side="right", padx=(5, 5))

        # Bottone per reset completo (soluzione drastica)
        self.reset_btn = ctk.CTkButton(
            self.buttons_frame,
            text="RESET GUI",
            command=self.reset_complete_gui,
            width=100,
            fg_color="orange",
            hover_color="darkorange",
            font=("Consolas", 11, "bold")
        )
        self.reset_btn.pack(side="right", padx=(5, 5))

        # Inizializza PowerShell
        self.start_powershell()

    def start_powershell(self):
        """Avvia una sessione PowerShell persistente con configurazione semplificata"""
        try:
            # Avvia PowerShell con configurazione semplificata per evitare errori di parsing
            self.process = subprocess.Popen(
                ["powershell.exe", 
                 "-NoExit", 
                 "-ExecutionPolicy", "Bypass", 
                 "-NoProfile", 
                 "-NoLogo",
                 "-Command", "-"
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                encoding='utf-8'
            )

            # Invia comandi di configurazione dopo l'avvio
            time.sleep(0.2)  # Attendi che PowerShell si avvii
            if self.process and self.process.stdin:
                try:
                    # Configura PowerShell per output pulito
                    init_commands = [
                        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8",
                        "$Host.UI.RawUI.WindowTitle = 'SHRI Terminal'",
                        "Clear-Host"
                    ]
                    for cmd in init_commands:
                        self.process.stdin.write(f"{cmd}\n")
                        self.process.stdin.flush()
                        time.sleep(0.1)
                except:
                    pass

            # Avvia il thread per leggere l'output
            self.output_thread = threading.Thread(target=self.read_output, daemon=True)
            self.output_thread.start()

            # Avvia il thread per aggiornare la GUI
            self.update_thread = threading.Thread(target=self.update_terminal, daemon=True)
            self.update_thread.start()

            self.write_to_terminal("🚀 Terminale PowerShell avviato\n", "info")

            # Controlla l'execution policy e mostra info utili
            self.check_execution_policy()

        except Exception as e:
            self.write_to_terminal(f"❌ Errore nell'avvio di PowerShell: {e}\n", "error")

    def read_output(self):
        """Legge l'output dal processo PowerShell con gestione specifica per prompt y/N"""
        if not self.process:
            return

        try:
            # Buffer per accumulo caratteri
            buffer = ""
            last_output_time = time.time()

            while self.process.poll() is None:
                try:
                    # Leggi carattere per carattere
                    char = self.process.stdout.read(1)
                    if char:
                        # Filtra caratteri di controllo più aggressivamente
                        # Permetti solo: caratteri stampabili (32-126), newline (10), tab (9), carriage return (13)
                        char_code = ord(char)
                        if char_code >= 32 or char_code in [9, 10, 13]:
                            buffer += char
                            last_output_time = time.time()

                        # Se troviamo un newline, invia sempre il buffer
                        if char == '\n':
                            if buffer:
                                # Pulisce caratteri di controllo residui e normalizza spazi
                                clean_buffer = ''.join(c for c in buffer if ord(c) >= 32 or c in ['\n', '\t', '\r'])
                                # Rimuove sequenze ANSI escape se presenti
                                import re
                                clean_buffer = re.sub(r'\x1b\[[0-9;]*m', '', clean_buffer)
                                self.output_queue.put(("output", clean_buffer))
                            buffer = ""
                        else:
                            # Pattern specifici che indicano prompt senza newline
                            prompt_patterns = [
                                'y/N:', 'y/n:', 'Y/N:', 'Y/n:',
                                'S/N:', 's/n:', 'S/n:', 's/N:',
                                '(y/n)', '(Y/N)', '(s/n)', '(S/N)',
                                'Press any key', 'Premere un tasto',
                                'Continue?', 'Continuare?',
                                'correct?', 'corretto?'
                            ]

                            # Se troviamo un pattern di prompt, invia immediatamente
                            if any(pattern in buffer for pattern in prompt_patterns):
                                clean_buffer = ''.join(c for c in buffer if ord(c) >= 32 or c in ['\n', '\t', '\r'])
                                import re
                                clean_buffer = re.sub(r'\x1b\[[0-9;]*m', '', clean_buffer)
                                self.output_queue.put(("output", clean_buffer))
                                buffer = ""

                            # Se il buffer finisce con : o ? ed è abbastanza lungo, probabilmente è un prompt
                            elif (buffer.endswith(':') or buffer.endswith('?')) and len(buffer.strip()) > 15:
                                clean_buffer = ''.join(c for c in buffer if ord(c) >= 32 or c in ['\n', '\t', '\r'])
                                import re
                                clean_buffer = re.sub(r'\x1b\[[0-9;]*m', '', clean_buffer)
                                self.output_queue.put(("output", clean_buffer))
                                buffer = ""
                    else:
                        # Nessun carattere disponibile
                        current_time = time.time()

                        # Se è passato più di 0.5 secondi senza output e c'è testo nel buffer
                        if (current_time - last_output_time) > 0.5 and buffer.strip():
                            clean_buffer = ''.join(c for c in buffer if ord(c) >= 32 or c in ['\n', '\t', '\r'])
                            self.output_queue.put(("output", clean_buffer))
                            buffer = ""

                        # Piccola pausa per non sovraccaricare la CPU
                        time.sleep(0.05)

                except Exception:
                    # In caso di errore, invia quello che c'è nel buffer
                    if buffer.strip():
                        clean_buffer = ''.join(c for c in buffer if ord(c) >= 32 or c in ['\n', '\t', '\r'])
                        self.output_queue.put(("output", clean_buffer))
                        buffer = ""
                    time.sleep(0.1)

        except Exception as e:
            self.output_queue.put(("error", f"Errore lettura output: {e}\n"))

    def update_terminal(self):
        """Aggiorna il terminale con l'output dalla coda"""
        while True:
            try:
                msg_type, content = self.output_queue.get(timeout=0.1)
                if msg_type == "output":
                    self.write_to_terminal(content, "output")
                elif msg_type == "error":
                    self.write_to_terminal(content, "error")
                elif msg_type == "info":
                    self.write_to_terminal(content, "info")
                elif msg_type == "refresh":
                    # Forza lo scroll quando il processo potrebbe essere in attesa di input
                    self.force_scroll()
            except queue.Empty:
                continue
            except Exception:
                break

    def force_scroll(self):
        """Forza lo scroll del terminale all'ultima posizione"""
        def scroll_update():
            try:
                self.terminal_output.see(tk.END)
                self.terminal_output.yview(tk.END)
                self.terminal_output.update_idletasks()

                # Aggiorna l'indicatore di stato quando sembra in attesa di input
                if hasattr(self, 'status_label'):
                    self.status_label.configure(text="⏳ In attesa input...", text_color="orange")

            except:
                pass

        # Esegui sulla GUI thread principale
        if hasattr(self.parent, 'after'):
            self.parent.after(0, scroll_update)

    def write_to_terminal(self, text, msg_type="output"):
        """Scrive testo nel terminale con colori diversi"""
        def update():
            self.terminal_output.config(state=tk.NORMAL)

            # Configura i tag per i colori con font più grandi
            if not hasattr(self, 'tags_configured'):
                self.terminal_output.tag_configure("output", foreground="#00ff00", font=("Consolas", 12))
                self.terminal_output.tag_configure("error", foreground="#ff5555", font=("Consolas", 12))
                self.terminal_output.tag_configure("info", foreground="#55aaff", font=("Consolas", 12))
                self.terminal_output.tag_configure("command", foreground="#ffff55", font=("Consolas", 12, "bold"))
                self.tags_configured = True

            # Limita il numero di righe nel terminale (mantiene le ultime 1000 righe)
            lines = self.terminal_output.get("1.0", tk.END).split('\n')
            if len(lines) > 1000:
                # Rimuovi le prime righe eccedenti
                self.terminal_output.delete("1.0", f"{len(lines) - 1000}.0")

            self.terminal_output.insert(tk.END, text, msg_type)

            # Forza lo scroll all'ultima linea con metodi multipli
            self.terminal_output.see(tk.END)
            self.terminal_output.yview(tk.END)

            # Assicura che il cursore sia alla fine
            self.terminal_output.mark_set(tk.INSERT, tk.END)

            self.terminal_output.config(state=tk.DISABLED)

            # Forza un aggiornamento della visualizzazione e dell'altezza
            self.terminal_output.update_idletasks()

            # Secondo passaggio di scroll dopo l'aggiornamento
            self.parent.after(1, lambda: self.terminal_output.see(tk.END))

            # Aggiorna l'indicatore di stato
            if hasattr(self, 'status_label') and text.strip():
                if msg_type == "command":
                    self.status_label.configure(text="⚡ Esecuzione...", text_color="yellow")
                elif msg_type == "output":
                    self.status_label.configure(text="✅ Attivo", text_color="green")

        # Esegui sulla GUI thread principale
        if hasattr(self.parent, 'after'):
            self.parent.after(0, update)

    def execute_command(self, event=None):
        """Esegue un comando nel terminale"""
        command = self.command_entry.get().strip()
        if not command:
            return

        self.command_entry.delete(0, tk.END)

        # Mostra il comando nel terminale
        self.write_to_terminal(f"PS> {command}\n", "command")

        if command.lower() in ['exit', 'quit']:
            self.close_terminal()
            return

        if command.lower() == 'clear':
            self.clear_terminal()
            return

        try:
            # Controlla se PowerShell è ancora attivo, altrimenti riavvialo
            if not self.process or self.process.poll() is not None:
                self.write_to_terminal("⚠️  PowerShell non attivo, riavvio...\n", "info")
                self.restart_powershell()
                time.sleep(0.5)  # Attendi che PowerShell si avvii

            if self.process and self.process.poll() is None:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
        except Exception as e:
            self.write_to_terminal(f"❌ Errore nell'esecuzione del comando: {e}\n", "error")

    def execute_script_command(self, command):
        """Esegue un comando script nel terminale (per i bottoni della GUI)"""
        self.write_to_terminal(f"PS> {command}\n", "command")

        # Traccia se è un comando che potrebbe avviare un processo lungo
        if any(keyword in command.lower() for keyword in ['python', 'pip', 'upload.py']):
            self.write_to_terminal("📍 Processo tracciato - usa 'Stop' per interromperlo\n", "info")

        try:
            if self.process and self.process.poll() is None:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
        except Exception as e:
            self.write_to_terminal(f"❌ Errore nell'esecuzione del comando: {e}\n", "error")

    def interrupt_process(self):
        """Invia Ctrl+C per terminare il processo corrente"""
        self.write_to_terminal("🛑 Tentativo di interruzione processo (Ctrl+C)...\n", "error")

        try:
            # Ctrl+C diretto nel processo PowerShell
            if self.process and self.process.poll() is None:
                # Metodo 1: Invio carattere Ctrl+C (0x03)
                if self.process.stdin:
                    self.process.stdin.write("\x03")
                    self.process.stdin.flush()
                    time.sleep(0.1)

                # Metodo 2: SIGINT (se disponibile)
                import signal
                try:
                    self.process.send_signal(signal.CTRL_C_EVENT)
                except:
                    pass

                # Metodo 3: Se ancora attivo, terminate()
                time.sleep(0.5)
                if self.process.poll() is None:
                    self.process.terminate()
                    time.sleep(0.2)
                    if self.process.poll() is None:
                        self.process.kill()

                self.write_to_terminal("✅ Processo interrotto!\n", "info")

                # Riavvia PowerShell automaticamente dopo l'interruzione
                self.write_to_terminal("🔄 Riavvio PowerShell...\n", "info")
                self.restart_powershell()

            else:
                self.write_to_terminal("ℹ️  Nessun processo attivo da interrompere\n", "info")

        except Exception as e:
            self.write_to_terminal(f"❌ Errore nell'interruzione: {e}\n", "error")
            # Fallback: force kill e riavvio
            try:
                if self.process:
                    self.process.kill()
                    self.write_to_terminal("⚡ Processo forzatamente terminato\n", "info")
                    self.write_to_terminal("🔄 Riavvio PowerShell...\n", "info")
                    self.restart_powershell()
            except:
                pass

    def restart_powershell(self):
        """Riavvia completamente PowerShell con kill aggressivo di tutti i processi"""
        try:
            self.write_to_terminal("🔄 Riavvio completo PowerShell in corso...\n", "info")

            # 1. Chiudi il processo esistente
            if self.process:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=1)
                except:
                    try:
                        self.process.kill()
                    except:
                        pass

            # 2. Kill aggressivo di tutti i PowerShell aperti da questo processo
            import subprocess
            try:
                subprocess.run(['taskkill', '/f', '/im', 'powershell.exe'], 
                             capture_output=True, timeout=5)
            except:
                pass

            # 3. Pulisce completamente il terminale
            self.terminal_output.config(state=tk.NORMAL)
            self.terminal_output.delete(1.0, tk.END)
            self.terminal_output.config(state=tk.DISABLED)

            # 4. Reset delle variabili
            self.process = None

            # 5. Attendi che tutto sia pulito
            time.sleep(1)

            # 6. Riavvia tutto da zero
            self.write_to_terminal("🧹 Sistema pulito, riavvio PowerShell...\n", "info")
            self.start_powershell()

            self.write_to_terminal("✅ PowerShell completamente riavviato!\n", "info")
            self.write_to_terminal("🎯 Sistema pronto per nuovi comandi\n", "info")

        except Exception as e:
            self.write_to_terminal(f"❌ Errore nel riavvio completo: {e}\n", "error")
            # Fallback estremo: suggerisci riavvio GUI
            self.write_to_terminal("⚠️  Consiglio: riavvia la GUI se i problemi persistono\n", "error")

    def reset_complete_gui(self):
        """Reset completo: riavvia l'intera applicazione"""
        import sys
        import os

        try:
            self.write_to_terminal("🔄 RESET COMPLETO DELLA GUI IN CORSO...\n", "error")

            # Killa tutti i processi PowerShell
            import subprocess
            try:
                subprocess.run(['taskkill', '/f', '/im', 'powershell.exe'], 
                             capture_output=True, timeout=5)
            except:
                pass

            # Chiudi il processo corrente
            if self.process:
                try:
                    self.process.kill()
                except:
                    pass

            self.write_to_terminal("⚡ Riavvio dell'applicazione in 2 secondi...\n", "info")

            # Schedula il riavvio dopo 2 secondi
            def restart_app():
                try:
                    # Chiude la finestra corrente
                    self.parent.destroy()

                    # Riavvia l'applicazione
                    python = sys.executable
                    script = os.path.abspath(__file__)
                    subprocess.Popen([python, script])

                except Exception as e:
                    print(f"Errore nel riavvio: {e}")

            # Esegui il riavvio dopo 2 secondi
            self.parent.after(2000, restart_app)

        except Exception as e:
            self.write_to_terminal(f"❌ Errore nel reset completo: {e}\n", "error")

    def clear_terminal(self):
        """Pulisce il contenuto del terminale"""
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.delete(1.0, tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        self.write_to_terminal("🧹 Terminale pulito\n", "info")

    def check_execution_policy(self):
        """Controlla e informa sull'execution policy"""
        self.write_to_terminal("ℹ️  Per evitare errori di execution policy, i comandi vengono eseguiti tramite CMD\n", "info")
        self.write_to_terminal("ℹ️  Se vedi errori PSReadline, sono normali e non influiscono sul funzionamento\n", "info")

    def close_terminal(self):
        """Chiude il terminale"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except:
                self.process.kill()
            self.process = None
        self.write_to_terminal("🔴 Terminale chiuso\n", "error")

    def pack(self, **kwargs):
        """Permette di usare pack() sul terminale"""
        self.terminal_frame.pack(**kwargs)

    def pack_forget(self):
        """Nasconde il terminale"""
        self.terminal_frame.pack_forget()

# === Dialog personalizzati ===
class CTkYesNoDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x180")
        self.resizable(False, False)
        self.result = False

        ctk.CTkLabel(self, text=message, wraplength=350).pack(pady=(30, 20))
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Sì", command=self.yes).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="No", command=self.no).pack(side="right", padx=10)

        self.grab_set()
        self.wait_window()

    def yes(self):
        self.result = True
        self.destroy()

    def no(self):
        self.result = False
        self.destroy()

# === CREAZIONE CONFIGURAZIONE ===
CONFIG_FILE = find_config_file()
selected_path = ""

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("SHRI - Upload Assistant GUI")
app.geometry("1400x1200")  # Finestra più grande per il font maggiore
app.resizable(True, True)

status_label = ctk.CTkLabel(app, text="", text_color="green")
status_label.pack(pady=10)

progress_bar = ctk.CTkProgressBar(app, width=400)
progress_bar.set(0)
progress_bar.pack(pady=(10, 0))
progress_bar.pack_forget()

# === FUNZIONI DI CONFIGURAZIONE ===
def save_config(bot_path: str, venv_path: str) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(f"{bot_path}\n{venv_path}")

def load_config() -> tuple[str | None, str | None]:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            if len(lines) >= 2:
                return lines[0], lines[1]
    return None, None

def resolve_activate_path(base_path):
    direct = os.path.join(base_path, "activate.bat")
    in_scripts = os.path.join(base_path, "Scripts", "activate.bat")
    if os.path.exists(direct):
        return direct
    elif os.path.exists(in_scripts):
        return in_scripts
    return None

def ask_for_paths():
    messagebox.showinfo("Configurazione manuale", "Seleziona la cartella dove si trova il BOT.")
    bot_path = filedialog.askdirectory(title="Cartella del bot Upload Assistant")
    if not bot_path:
        messagebox.showerror("Errore", "Devi selezionare la cartella del bot.")
        app.destroy()
        exit()

    messagebox.showinfo("Configurazione manuale", "Ora seleziona la cartella del virtual environment (es: venv o Scripts).")
    venv_path = filedialog.askdirectory(title="Cartella del virtual environment o 'Scripts'")
    activate_path = resolve_activate_path(venv_path)

    if not venv_path or not activate_path:
        messagebox.showerror("Errore", "Cartella virtual environment non valida.")
        app.destroy()
        exit()

    save_config(bot_path, venv_path)
    return bot_path, venv_path

def patch_config(content: str, keys: dict) -> str:
    # Escape delle API keys per evitare problemi con backreferences regex
    def escape_for_regex(value):
        """Escape dei caratteri speciali per l'uso in regex replacement"""
        if not value:
            return value
        # Escape dei backslashes per evitare interpretazione come backreferences
        return value.replace('\\', '\\\\')
    
    # Escape di tutte le keys che potrebbero contenere caratteri speciali
    tmdb_api_escaped = escape_for_regex(keys.get("tmdb_api", ""))
    imgbb_api_escaped = escape_for_regex(keys.get("imgbb_api", ""))
    qbit_url_escaped = escape_for_regex(keys.get("qbit_url", "http://127.0.0.1"))
    qbit_port_escaped = escape_for_regex(keys.get("qbit_port", "8080"))
    qbit_user_escaped = escape_for_regex(keys.get("qbit_user", ""))
    qbit_pass_escaped = escape_for_regex(keys.get("qbit_pass", ""))
    shri_api_escaped = escape_for_regex(keys.get("shri_api", ""))
    
    content = re.sub(r'"tmdb_api"\s*:\s*".*?"', f'"tmdb_api": "{tmdb_api_escaped}"', content)
    content = re.sub(r'"imgbb_api"\s*:\s*".*?"', f'"imgbb_api": "{imgbb_api_escaped}"', content)
    content = re.sub(r'"qbit_url"\s*:\s*".*?"', f'"qbit_url": "{qbit_url_escaped}"', content)
    content = re.sub(r'"qbit_port"\s*:\s*".*?"', f'"qbit_port": "{qbit_port_escaped}"', content)
    content = re.sub(r'"qbit_user"\s*:\s*".*?"', f'"qbit_user": "{qbit_user_escaped}"', content)
    content = re.sub(r'"qbit_pass"\s*:\s*".*?"', f'"qbit_pass": "{qbit_pass_escaped}"', content)
    content = re.sub(r'"tone_map"\s*:\s*True', '"tone_map": False', content)
    
    # Fix per evitare errori "invalid group reference" quando l'API key contiene backslashes seguiti da numeri
    content = re.sub(r'(\"SHRI\"\s*:\s*\{.*?)("api_key"\s*:\s*\").*?(\")', r'\1\2' + shri_api_escaped + r'\3', content, flags=re.DOTALL)
    content = content.replace('"add_logo": False', '"add_logo": True')
    content = content.replace('"logo_language": ""', '"logo_language": "it"')
    content = content.replace('"img_host_1": ""', '"img_host_1": "ptscreens"')
    content = content.replace('"img_host_2": ""', '"img_host_2": "imgbox"')
    content = content.replace('"screens": "4"', '"screens": "6"')
    content = content.replace('"multiScreens": "2"', '"multiScreens": "0"')
    content = content.replace('"search_requests": "False"', '"search_requests": "True"')
    content = content.replace('"use_italian_title": False', '"use_italian_title": True')
    return content

def setup_from_local():
    """Setup: usa Upload-Assistant locale se presente, altrimenti lo clona automaticamente dalla repo di Audionut."""
    progress_bar.pack(pady=(10, 0))
    progress_bar.set(0.0)
    status_label.configure(text="🔍 Preparazione setup locale...", text_color="yellow")
    app.update()

    repo_root = os.path.abspath(os.path.dirname(__file__))
    detected_bot = os.path.join(repo_root, "Upload-Assistant")

    bot_path = None
    # Se troviamo Upload-Assistant nella stessa repo, chiediamo se usarla
    if os.path.exists(detected_bot) and os.path.isdir(detected_bot):
        dialog = CTkYesNoDialog(app, "Cartella trovata", f"Ho trovato Upload-Assistant in:\n{detected_bot}\nVuoi usarla per il setup?")
        if dialog.result:
            bot_path = detected_bot

    if not bot_path:
        # chiedi all'utente la root dove vuole installare/clonare Upload-Assistant
        messagebox.showinfo("Setup automatico", "Seleziona la cartella root dove vuoi installare Upload-Assistant.")
        target_dir = filedialog.askdirectory(title="Cartella root per Upload-Assistant")
        if not target_dir:
            messagebox.showerror("Errore", "Cartella non selezionata. Impossibile continuare.")
            app.destroy()
            exit()

        candidate = os.path.join(target_dir, "Upload-Assistant")
        if not os.path.exists(candidate) or not os.path.isdir(candidate):
            # Clona la repo di Audionut
            status_label.configure(text="🔀 Clonazione Upload-Assistant...", text_color="yellow")
            app.update()
            process = subprocess.run(["git", "clone", "https://github.com/Audionut/Upload-Assistant.git"], cwd=target_dir)
            if process.returncode != 0:
                messagebox.showerror("Errore", "Errore durante la clonazione della repository Upload-Assistant.")
                app.destroy()
                exit()
            candidate = os.path.join(target_dir, "Upload-Assistant")
            if not os.path.exists(candidate) or not os.path.isdir(candidate):
                messagebox.showerror("Errore", "Clonazione fallita: non trovo la cartella Upload-Assistant.")
                app.destroy()
                exit()
        bot_path = candidate

    progress_bar.set(0.2)
    app.update()
    venv_path = os.path.join(bot_path, ".venv")

    status_label.configure(text="🔧 Creazione ambiente virtuale...", text_color="yellow")
    app.update()
    subprocess.run(f'python -m venv "{venv_path}"', shell=True)

    progress_bar.set(0.4)
    app.update()

    activate_path = resolve_activate_path(venv_path)
    if not activate_path:
        messagebox.showerror("Errore", "Virtual environment non trovato.")
        app.destroy()
        exit()

    status_label.configure(text="⚙️ Configurazione file...", text_color="yellow")
    app.update()

    example_cfg = os.path.join(bot_path, "data", "example-config.py")
    target_cfg = os.path.join(bot_path, "data", "config.py")

    # Trova o seleziona il file api_keys.json
    keys_file = find_or_select_api_keys()
    if not keys_file:
        messagebox.showerror("Errore", "File api_keys.json richiesto per continuare!")
        app.destroy()
        exit()

    # Valida e compila eventuali API keys mancanti
    keys = validate_and_fill_api_keys(keys_file)
    if keys is None:
        messagebox.showinfo("Operazione annullata", "Setup annullato dall'utente.")
        app.destroy()
        exit()

    try:
        with open(example_cfg, "r", encoding="utf-8") as f:
            content = f.read()

        content = patch_config(content, keys)

        with open(target_cfg, "w", encoding="utf-8") as f:
            f.write(content)

    except Exception as e:
        messagebox.showerror("Errore", f"Errore leggendo o modificando api_keys.json:\n{e}")
        app.destroy()
        exit()

    progress_bar.set(0.7)
    app.update()

    status_label.configure(text="📦 Installazione dipendenze...", text_color="yellow")
    app.update()
    subprocess.run(f'cmd.exe /c "cd /d \"{bot_path}\" && call \"{activate_path}\" && pip install -r requirements.txt"', shell=True)

    progress_bar.set(1.0)
    status_label.configure(text="✅ Setup completato!", text_color="green")
    app.update()

    save_config(bot_path, venv_path)
    progress_bar.pack_forget()
    app.update()

    return bot_path, venv_path

# === INIZIO APPLICAZIONE ===
def get_valid_paths() -> tuple[str, str]:
    temp_bot_path, temp_venv_path = load_config()

    if not temp_bot_path or not temp_venv_path or not resolve_activate_path(temp_venv_path):
        dialog = CTkYesNoDialog(app, "Setup iniziale", "Il bot non è ancora configurato. Vuoi eseguire il setup automatico?")
        if dialog.result:
            return setup_from_local()
        else:
            return ask_for_paths()
    return temp_bot_path, temp_venv_path

bot_path, venv_path = get_valid_paths()
activate_path = resolve_activate_path(venv_path)
assert activate_path is not None, "Percorso di attivazione non trovato"

# Inizializza il terminale integrato
terminal = IntegratedTerminal(app)

# === FUNZIONI APPLICAZIONE ===
def select_path():
    global selected_path
    release_type = release_option.get()

    path = None
    if release_type in ["Film (MKV)", "Serie (Episodio)"]:
        path = filedialog.askopenfilename(filetypes=[("MKV files", "*.mkv")])
    elif release_type in ["Serie (Stagione)", "Film (Disco)"]:
        path = filedialog.askdirectory(title=f"Seleziona una cartella per: {release_type}")

    if path:
        selected_path = path
        path_label.configure(text=os.path.basename(path))
    else:
        selected_path = ""
        path_label.configure(text="Nessuna selezione")

def open_config_py():
    config_path = os.path.join(bot_path, "data", "config.py")
    if not os.path.exists(config_path):
        messagebox.showerror("Errore", "Il file config.py non esiste.")
        return

    try:
        # Proviamo ad aprire con Notepad++
        subprocess.Popen(r'"C:\Program Files\Notepad++\notepad++.exe" "' + config_path + '"')
    except FileNotFoundError:
        # Se Notepad++ non è trovato, ripiega su Notepad
        subprocess.Popen(f'notepad.exe "{config_path}"')
    except Exception as e:
        messagebox.showerror("Errore", f"Impossibile aprire config.py\n{e}")

def run_git_pull():
    progress_bar.set(0.0)
    status_label.configure(text="🔄 Controllo aggiornamenti Bot...", text_color="yellow")
    app.update()

    # Cambia directory e esegue git pull nel terminale integrato
    terminal.execute_script_command(f'cd "{bot_path}"')
    terminal.execute_script_command('git pull')

    progress_bar.set(1.0)
    status_label.configure(text="✅ Comando git pull inviato", text_color="green")

def run_pip_install():
    progress_bar.set(0.0)
    status_label.configure(text="🔄 Controllo aggiornamenti pip...", text_color="yellow")
    app.update()

    # Attiva l'ambiente virtuale e installa i requirements nel terminale integrato
    terminal.execute_script_command(f'cd "{bot_path}"')
    # Usa l'operatore & di PowerShell per eseguire comandi con percorsi che contengono spazi
    if venv_path:
        pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
        if os.path.exists(pip_exe):
            terminal.execute_script_command(f'& "{pip_exe}" install -r requirements.txt')
        else:
            terminal.execute_script_command('pip install -r requirements.txt')
    else:
        terminal.execute_script_command('pip install -r requirements.txt')

    progress_bar.set(1.0)
    status_label.configure(text="✅ Comando pip install inviato", text_color="green")

def run_upload():
    if not selected_path or not os.path.exists(selected_path):
        status_label.configure(text="❌ Percorso non valido", text_color="red")
        return

    tracker = tracker_option.get().strip().upper()
    imdb_id = imdb_entry.get().strip()
    tmdb_id = tmdb_entry.get().strip()
    tag_value = tag_entry.get().strip()
    service_value = service_entry.get().strip()
    edition_value = edition_entry.get().strip()

    # Controllo checkbox seed
    do_seed = seed_var.get()
    if do_seed:
        upload_cmd = f'python upload.py "{selected_path}" --skip_auto_torrent --trackers {tracker} --cleanup'
    else:
        upload_cmd = f'python upload.py "{selected_path}" --skip_auto_torrent --no-seed --trackers {tracker} --cleanup'

    if imdb_id:
        upload_cmd += f" --imdb {imdb_id}"
    if tmdb_id:
        upload_cmd += f" --tmdb {tmdb_id}"
    if tag_value:
        upload_cmd += f" --tag {tag_value}"
    if service_value:
        upload_cmd += f" --service {service_value}"
    if edition_value:
        upload_cmd += f" --edition {edition_value}"

    # Esegue l'upload nel terminale integrato
    terminal.execute_script_command(f'cd "{bot_path}"')
    # Usa l'operatore & di PowerShell per eseguire l'eseguibile Python dell'ambiente virtuale
    if venv_path:
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
        if os.path.exists(python_exe):
            # Sostituisce 'python' con il percorso completo usando l'operatore &
            upload_cmd_with_venv = upload_cmd.replace('python ', f'& "{python_exe}" ')
            terminal.execute_script_command(upload_cmd_with_venv)
        else:
            terminal.execute_script_command(upload_cmd)
    else:
        terminal.execute_script_command(upload_cmd)

    status_label.configure(text="✅ Upload avviato nel terminale...", text_color="green")

# === LAYOUT ===
ctk.CTkLabel(app, text="Seleziona il tipo di rilascio").pack(pady=(15, 0))
release_option = ctk.CTkComboBox(app, values=["Film (MKV)",  "Film (Disco)", "Serie (Episodio)", "Serie (Stagione)"], width=180)
release_option.set("")
release_option.pack(pady=5)
ToolTip(release_option, "Scegli se caricare:\n- un film (singolo file)\n- un episodio\n- un'intera stagione (cartella)\n- una cartella BluRay (es. BDMV)")

select_btn = ctk.CTkButton(app, text="Seleziona", command=select_path)
select_btn.pack(pady=5)
ToolTip(select_btn, "Seleziona un file .mkv o una cartella a seconda del tipo scelto.")

path_label = ctk.CTkLabel(app, text="Non hai effettuato nessuna selezione")
path_label.pack(pady=5)

ctk.CTkLabel(app, text="Tracker").pack(pady=(10, 0))
tracker_option = ctk.CTkComboBox(app, values=["SHRI"], width=120)
tracker_option.set("")
tracker_option.pack(pady=5)
ToolTip(tracker_option, "Seleziona il tracker dove vuoi caricare il file.")

imdb_entry = ctk.CTkEntry(app, placeholder_text="IMDb ID (opzionale)", width=240)
imdb_entry.pack(pady=5)
ToolTip(imdb_entry, "Inserisci l'ID IMDb (opzionale) da imdb.com\nEsempio: tt0068646 per Il Padrino.")

tmdb_entry = ctk.CTkEntry(app, placeholder_text="TMDB ID (opzionale)", width=240)
tmdb_entry.pack(pady=5)
ToolTip(tmdb_entry, "Inserisci l'ID TMDB (opzionale) da TMDB.org\nEsempio: 550 per Fight Club.")

tag_entry = ctk.CTkEntry(app, placeholder_text="TAG gruppo (opzionale)", width=240)
tag_entry.pack(pady=5)
ToolTip(tag_entry, "Inserisci TAG della Crew (opzionale)\nEsempio: G66, iSlaNd, LFi")

service_entry = ctk.CTkEntry(app, placeholder_text="Piattaforma di streaming (opzionale)", width=240)
service_entry.pack(pady=5)
ToolTip(service_entry, "Inserisci un nome servizio per il rilascio\n(es. NF, AMZN, ATVP, DSNP, NOW).")

edition_entry = ctk.CTkEntry(app, placeholder_text="Aggiungi edizione (opzionale)", width=240)
edition_entry.pack(pady=5)
ToolTip(edition_entry, "Inserisci una versione speciale del film (opzionale).\nEsempio: HYBRID, Extended, Remastered, Director's Cut.")


# Checkbox per seed torrent
seed_var = tk.BooleanVar(value=False)
seed_checkbox = ctk.CTkCheckBox(app, text="Fai seed del torrent dopo l'upload", variable=seed_var)
seed_checkbox.pack(pady=20)
ToolTip(seed_checkbox, "Se selezionato, il torrent verrà seedato dopo l'upload. Di default è NO.")

upload_btn = ctk.CTkButton(app, text="Upload", command=run_upload)
upload_btn.pack(pady=10)
ToolTip(upload_btn, "Avvia il comando di upload con i parametri selezionati.")

git_btn = ctk.CTkButton(app, text="Controlla aggiornamenti Upload-Assistant", command=run_git_pull, fg_color="green", hover_color="darkgreen", text_color="white")
git_btn.pack(pady=5)
ToolTip(git_btn, "Esegui un git pull per aggiornare lo script all'ultima versione.")

pip_btn = ctk.CTkButton(app, text="Controlla aggiornamenti dipendenze", command=run_pip_install, fg_color="green", hover_color="darkgreen", text_color="white")
pip_btn.pack(pady=5)
ToolTip(pip_btn, "Esegui pip install per aggiornare le dipendenze del progetto.")

config_btn = ctk.CTkButton(app, text="Modifica Config.py", command=open_config_py, fg_color="blue", hover_color="darkblue", text_color="white")
config_btn.pack(pady=5)
ToolTip(config_btn, "Apri il file config.py per modificare la configurazione del bot.")

progress_bar = ctk.CTkProgressBar(app, width=400)
progress_bar.set(0)
progress_bar.pack(pady=(10, 0))

status_label = ctk.CTkLabel(app, text="", text_color="green")
status_label.pack(pady=10)

# Aggiungi il terminale alla GUI
terminal.pack(fill="both", expand=True, padx=10, pady=10)

# Funzione per chiudere il terminale quando l'app viene chiusa
def on_closing():
    terminal.close_terminal()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_closing)

ctk.CTkLabel(app, text="Authors: Tiberio87").pack(pady=5)

app.mainloop()