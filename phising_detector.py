import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
from bs4 import BeautifulSoup  # <-- NUOVO IMPORT

# 1. Caricamento API Key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Attenzione: Chiave API non trovata nel file .env!")

genai.configure(api_key=API_KEY)

# --- NUOVA FUNZIONE: Estrazione dati dall'HTML ---
def estrai_dati_html(html_grezzo):
    print("🧹 Estrazione testo e link dall'HTML in corso...")
    soup = BeautifulSoup(html_grezzo, "html.parser")
    
    # Estraiamo tutto il testo visibile
    testo_visibile = soup.get_text(separator="\n", strip=True)
    
    # Estraiamo tutti i link (href) nascosti nei tag <a>
    link_trovati = [a.get('href') for a in soup.find_all('a', href=True)]
    
    # Prepariamo un pacchetto pulito per Gemini
    dati_per_gemini = f"""
    TESTO DELL'EMAIL:
    {testo_visibile}
    
    LINK TROVATI NELL'EMAIL:
    {link_trovati}
    """
    return dati_per_gemini

# --- FUNZIONE PRINCIPALE (Aggiornata con istruzioni sui link) ---
def analizza_phishing(dati_puliti):
    print("⏳ Analisi di sicurezza in corso tramite Gemini...\n")
    model = genai.GenerativeModel('gemini-2.5-flash')
    
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
        "motivo": "breve spiegazione del perché, citando eventuali link sospetti"
    }}
    """
    
    try:
        risposta = model.generate_content(prompt)
        testo_pulito = risposta.text.replace('```json', '').replace('```', '').strip()
        risultato = json.loads(testo_pulito)
        return risultato

    except Exception as e:
        return {"errore": str(e)}

# --- ZONA DI TEST CON HTML REALE ---

# Una finta email HTML con un bottone che nasconde un link malevolo
email_html_grezza = """
<html>
<head>
<style>
  body { font-family: Arial, sans-serif; background-color: #f4f4f4; text-align: center; }
  .container { background-color: #ffffff; width: 80%; margin: 30px auto; border: 3px solid #FFD700; padding: 20px; border-radius: 10px; }
  h1 { color: #d35400; font-size: 3em; margin-bottom: 10px; }
  h2 { color: #2ecc71; }
  .prize-box { background-color: #f1c40f; padding: 20px; font-size: 24px; font-weight: bold; color: #fff; margin: 20px 0; }
  .claim-btn { background-color: #e74c3c; color: white; font-size: 20px; padding: 20px 40px; text-decoration: none; border-radius: 50px; border: 5px solid #c0392b; display: inline-block; }
</style>
</head>
<body>
  <div class="container">
    <h1>CONGRATULAZIONI!</h1>
    <h2>Sei stato selezionato casualmente!</h2>
    <p>Gentile utente Amazon,</p>
    <p>In occasione del nostro anniversario, abbiamo estratto il tuo indirizzo email come vincitore del premio fedeltà di questo mese.</p>
    
    <div class="prize-box">
      IL TUO PREMIO: BUONO AMAZON DA 500€
    </div>
    
    <p>Attenzione: Hai solo <b>3 ore</b> per reclamare il tuo premio prima che venga riassegnato ad un altro utente.</p>
    
    <a href="http://bit.ly/claim-prize-amazon-f4k3" class="claim-btn">
      👉 CLICCA QUI PER RISCATTARE I TUOI 500€ ORA 👈
    </a>
    
    <p style="font-size: 10px; color: #999; margin-top: 30px;">*Termini e condizioni applicabili. Non affiliato direttamente con Amazon Inc.</p>
  </div>
</body>
</html>
"""

# 1. Prima passiamo l'HTML grezzo a BeautifulSoup
dati_estratti = estrai_dati_html(email_html_grezza)

# 2. Poi passiamo i dati estratti a Gemini
esito = analizza_phishing(dati_estratti)

# Stampiamo il risultato a schermo
print("--- RISULTATO ANALISI ---")
print(f"È Phishing?: {esito.get('is_phishing')}")
print(f"Punteggio di Rischio: {esito.get('score_rischio')}/100")
print(f"Motivazione: {esito.get('motivo')}")