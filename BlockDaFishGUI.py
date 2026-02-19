import os
import threading
import json
import customtkinter as ctk
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai

# --- CONFIGURAZIONE INIZIALE ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

# --- FUNZIONI DI LOGICA (Dal codice originale) ---
def estrai_dati_html(html_grezzo):
    soup = BeautifulSoup(html_grezzo, "html.parser")
    testo_visibile = soup.get_text(separator="\n", strip=True)
    link_trovati = [a.get('href') for a in soup.find_all('a', href=True)]
    
    return f"""
    TESTO DELL'EMAIL:
    {testo_visibile}
    
    LINK TROVATI NELL'EMAIL:
    {link_trovati}
    """

def analizza_phishing(dati_puliti):
    if not API_KEY:
        return {"errore": "API Key mancante. Controlla il file .env"}
        
    model = genai.GenerativeModel('gemini-flash-latest')
    prompt = f"""
    Sei un analista di cybersecurity. Analizza il seguente contenuto di un'email (testo e link estratti) per capire se è phishing.
    Presta particolare attenzione se i link sembrano sospetti, offuscati o non corrispondono a domini ufficiali.
    
    CONTENUTO EMAIL:
    {dati_puliti}
    
    REGOLE DI RISPOSTA:
    Devi rispondere SOLO con un oggetto JSON valido. Struttura:
    {{
        "is_phishing": true/false,
        "score_rischio": numero da 1 a 100,
        "motivo": "breve spiegazione del perché"
    }}
    """
    try:
        risposta = model.generate_content(prompt)
        testo_pulito = risposta.text.replace('```json', '').replace('```', '').strip()
        return json.loads(testo_pulito)
    except Exception as e:
        return {"errore": str(e)}

# --- INTERFACCIA GRAFICA (GUI) ---

class AppPhishing(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Impostazioni finestra principale
        self.title("BlockDaFish")
        self.geometry("800x600")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Titolo
        self.lbl_titolo = ctk.CTkLabel(self, text="Analizzatore Anti-Phishing", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_titolo.pack(pady=(20, 10))

        # ---Contenitore orizzontale per Istruzioni + Bottone Incolla ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(fill="x", padx=20, pady=(0, 5))

        self.lbl_istruzioni = ctk.CTkLabel(self.frame_top, text="Incolla qui il codice HTML grezzo dell'email:")
        self.lbl_istruzioni.pack(side="left")
        
        # Il nuovo bottone "Incolla"
        self.btn_incolla = ctk.CTkButton(self.frame_top, text="📋 Incolla dagli Appunti", width=150, height=28, command=self.incolla_dagli_appunti)
        self.btn_incolla.pack(side="right")
        # -------------------------------------------------------------------------

        # Box di testo per l'HTML
        self.txt_input = ctk.CTkTextbox(self, height=200)
        self.txt_input.pack(fill="x", padx=20, pady=(5, 15))

        # Bottone di avvio analisi
        self.btn_analizza = ctk.CTkButton(self, text="🔍 Analizza Email", command=self.avvia_analisi, height=40, font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_analizza.pack(pady=10)

        # Frame per i risultati
        self.frame_risultati = ctk.CTkFrame(self)
        self.frame_risultati.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_esito = ctk.CTkLabel(self.frame_risultati, text="Esito: In attesa...", font=ctk.CTkFont(size=18))
        self.lbl_esito.pack(pady=(10, 5))

        self.lbl_punteggio = ctk.CTkLabel(self.frame_risultati, text="Rischio: --/100", font=ctk.CTkFont(size=16))
        self.lbl_punteggio.pack(pady=5)

        self.txt_motivo = ctk.CTkTextbox(self.frame_risultati, height=80, wrap="word", state="disabled")
        self.txt_motivo.pack(fill="x", padx=10, pady=(5, 10))

    # --- Funzione che legge gli appunti ---
    def incolla_dagli_appunti(self):
        try:
            # Legge cosa c'è copiato nel sistema
            testo_appunti = self.clipboard_get()
            
            # Svuota prima il box per evitare di incollare sopra roba vecchia
            self.txt_input.delete("1.0", "end")
            
            # Inserisce il nuovo testo
            self.txt_input.insert("1.0", testo_appunti)
        except Exception:
            # Se gli appunti sono vuoti o contengono un'immagine anziché testo
            self.mostra_errore("Gli appunti sono vuoti o non contengono testo valido.")

    # --- LOGICA DELL'INTERFACCIA ---
    def avvia_analisi(self):
        html_grezzo = self.txt_input.get("1.0", "end-1c").strip()
        if not html_grezzo:
            self.mostra_errore("Per favore, incolla del codice HTML prima di analizzare.")
            return

        self.btn_analizza.configure(text="⏳ Analisi in corso...", state="disabled")
        self.lbl_esito.configure(text="Analizzando i dati tramite Gemini...", text_color="white")
        self.lbl_punteggio.configure(text="Rischio: --/100", text_color="white")
        self.aggiorna_motivo("")

        thread = threading.Thread(target=self.processa_dati, args=(html_grezzo,))
        thread.start()

    def processa_dati(self, html_grezzo):
        dati_estratti = estrai_dati_html(html_grezzo)
        risultato = analizza_phishing(dati_estratti)
        self.after(0, self.mostra_risultati, risultato)

    def mostra_risultati(self, risultato):
        self.btn_analizza.configure(text="🔍 Analizza Email", state="normal")

        if "errore" in risultato:
            self.mostra_errore(risultato["errore"])
            return

        is_phishing = risultato.get("is_phishing", False)
        score = risultato.get("score_rischio", 0)
        motivo = risultato.get("motivo", "Nessuna motivazione fornita.")

        if is_phishing:
            self.lbl_esito.configure(text="⚠️ ATTENZIONE: Possibile Phishing!", text_color="#ff4a4a")
            self.lbl_punteggio.configure(text=f"Rischio: {score}/100", text_color="#ff4a4a")
        else:
            self.lbl_esito.configure(text="✅ Email Sicura", text_color="#00d15e")
            self.lbl_punteggio.configure(text=f"Rischio: {score}/100", text_color="#00d15e")

        self.aggiorna_motivo(f"MOTIVAZIONE:\n{motivo}")

    def mostra_errore(self, messaggio):
        self.lbl_esito.configure(text="❌ Errore", text_color="red")
        self.lbl_punteggio.configure(text="Rischio: --/100", text_color="white")
        self.aggiorna_motivo(messaggio)
        self.btn_analizza.configure(text="🔍 Analizza Email", state="normal")

    def aggiorna_motivo(self, testo):
        self.txt_motivo.configure(state="normal")
        self.txt_motivo.delete("1.0", "end")
        self.txt_motivo.insert("1.0", testo)
        self.txt_motivo.configure(state="disabled")

# --- AVVIO DELL'APP ---
if __name__ == "__main__":
    app = AppPhishing()
    app.mainloop()
