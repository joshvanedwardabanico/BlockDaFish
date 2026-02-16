# 🎣 Phishing Email Detector (Powered by Gemini API)

Un semplice ma potente script in Python per l'analisi semantica delle email. Utilizza l'intelligenza artificiale (Gemini) e l'estrazione dati (BeautifulSoup) per rilevare tentativi di spear-phishing e social engineering a partire dal codice HTML grezzo delle email.

## 🚀 Funzionalità

- **Parsing HTML:** Estrae automaticamente il testo pulito e tutti i link (tag `<a>`) nascosti nel codice sorgente dell'email.
- **Analisi Semantica Avanzata:** Valuta il tono, il senso di urgenza artificiale e le incongruenze nel testo.
- **Ispezione URL:** Segnala domini sospetti o offuscati presenti nel corpo del messaggio.
- **Output Strutturato:** Restituisce un JSON con il punteggio di rischio, l'esito booleano e la motivazione dettagliata.

## 🛠️ Prerequisiti

- Python 3.x
- Una chiave API valida di Google Gemini (ottenibile gratuitamente su [Google AI Studio](https://aistudio.google.com/))

## 📦 Installazione

1. **Crea e attiva un ambiente virtuale:**
   ```bash
   python -m venv venv
   # Su Windows:
   .\venv\Scripts\activate
   # Su Mac/Linux:
   source venv/bin/activate
   ```
2. **Installa le dipendenze necessarie:**

```bash
pip install google-generativeai beautifulsoup4 python-dotenv
```
3. **Configura la chiave API:**
Crea un file chiamato .env nella directory principale del progetto e inserisci la tua chiave in questo formato:

```bash
GEMINI_API_KEY="INSERISCI_QUI_LA_TUA_CHIAVE"
```
## 💻 Utilizzo
Per avviare l'analisi, esegui semplicemente lo script dal terminale:

```bash
python phishing_detector.py
```

Esempio di Output:
JSON

```bash
--- RISULTATO ANALISI ---
È Phishing?: True
Punteggio di Rischio: 95/100
Motivazione: Il testo presenta un falso senso di urgenza (scadenza di 30 minuti) per forzare l'utente all'azione. Inoltre, il link fornito ([http://secure-admin-login-update-123.xyz/login](http://secure-admin-login-update-123.xyz/login)) utilizza un dominio non ufficiale e altamente sospetto (.xyz) che non corrisponde a un reale pannello amministrativo.
```
