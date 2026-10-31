import os
import streamlit as st
import requests

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="Crypto Signal Lab",
    page_icon="📈",
    layout="wide"
)

st.title("🚀 Crypto Signal Lab - AI Trading Dashboard")
st.markdown("Dashboard interattiva per l'analisi e la generazione di segnali crypto tramite **Gemini** e **Groq**.")

# Sidebar per la configurazione delle API e dei parametri
st.sidebar.header("⚙️ Configurazione")

# Recupera le chiavi dalle variabili d'ambiente (impostate su Render) o dai campi di input
gemini_key = os.getenv("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")
groq_key = os.getenv("GROQ_API_KEY") or st.sidebar.text_input("Groq API Key", type="password")

# Selezione della criptovaluta e del modello
crypto_symbol = st.sidebar.selectbox("Seleziona Crypto", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"])
ai_provider = st.sidebar.radio("Seleziona Intelligenza Artificiale", ["Google Gemini", "Groq"])

st.sidebar.markdown("---")
analyze_button = st.sidebar.button("Genera Analisi e Segnale")

# Funzione per recuperare il prezzo attuale da Binance (pubblico, senza API key)
def get_crypto_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        return None

current_price = get_crypto_price(crypto_symbol)

# Area Principale della Dashboard
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📊 Asset: {crypto_symbol}")
    if current_price:
        st.metric(label="Prezzo Corrente (USD)", value=f"${current_price:,.2f}")
    else:
        st.warning("Impossibile recuperare il prezzo in tempo reale.")

with col2:
    st.subheader("ℹ️ Stato del Servizio")
    st.success("🟢 Sistema Online e Operativo su Render")

st.markdown("---")

# Sezione di analisi IA
if analyze_button:
    if ai_provider == "Google Gemini" and not gemini_key:
        st.error("⚠️ Inserisci la chiave API di Gemini per procedere.")
    elif ai_provider == "Groq" and not groq_key:
        st.error("⚠️ Inserisci la chiave API di Groq per procedere.")
    else:
        with st.spinner(f"Analisi di mercato in corso con {ai_provider}..."):
            prompt_testo = f"Analizza la criptovaluta {crypto_symbol} che quota attualmente ${current_price}. Fornisci un'indicazione sintetica di trading (BUY, SELL o HOLD) con motivazione tecnica."
            
            try:
                if ai_provider == "Google Gemini":
                    # Utilizzo della libreria google-genai
                    from google import genai
                    client = genai.Client(api_key=gemini_key)
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_testo,
                    )
                    risultato_ia = response.text
                else:
                    # Utilizzo delle API di Groq via requests
                    headers = {
                        "Authorization": f"Bearer {groq_key}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt_testo}]
                    }
                    response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=10)
                    res_json = response.json()
                    risultato_ia = res_json['choices'][0]['message']['content']

                st.subheader("🤖 Risultato Analisi IA")
                st.write(risultato_ia)
                
            except Exception as e:
                st.error(f❌ Errore durante la generazione della risposta: {e}")
else:
    st.info("👈 Configura le chiavi, seleziona l'asset e clicca su **Genera Analisi e Segnale** dalla barra laterale.")
