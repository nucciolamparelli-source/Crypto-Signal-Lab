import os
import streamlit as st
import requests

st.set_page_config(
    page_title="Crypto Signal Lab",
    page_icon="📈",
    layout="wide"
)

st.title("🚀 Crypto Signal Lab - AI Trading Dashboard")
st.markdown("Dashboard avanzata per l'analisi e la generazione di segnali crypto tramite **Gemini**.")

# Sidebar per configurazione e personalizzazione
st.sidebar.header("⚙️ Configurazione & Parametri")

gemini_key = os.getenv("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")

# Selezione estesa di criptovalute
crypto_options = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT"]
crypto_symbol = st.sidebar.selectbox("Seleziona Crypto", crypto_options)

# Parametri di analisi personalizzabili
trading_style = st.sidebar.selectbox("Stile di Trading", ["Day Trading (Breve termine)", "Swing Trading (Medio termine)", "HODL / Investimento (Lungo termine)"])
risk_level = st.sidebar.selectbox("Profilo di Rischio", ["Conservativo", "Bilanciato", "Aggressivo"])

st.sidebar.markdown("---")
analyze_button = st.sidebar.button("Genera Analisi Avanzata")

# Funzione per recuperare il prezzo da Binance
def get_crypto_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        return None

current_price = get_crypto_price(crypto_symbol)

# Layout principale
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📊 Asset: {crypto_symbol}")
    if current_price:
        st.metric(label="Prezzo Corrente (USD)", value=f"${current_price:,.2f}")
    else:
        st.warning("Impossibile recuperare il prezzo in tempo reale.")

with col2:
    st.subheader("⚙️ Parametri Selezionati")
    st.info(f"**Stile:** {trading_style} \n\n **Rischio:** {risk_level}")

st.markdown("---")

if analyze_button:
    if not gemini_key:
        st.error("⚠️ Inserisci la chiave API di Gemini nella barra laterale per procedere.")
    else:
        with st.spinner(f"Analisi di {crypto_symbol} in corso con Gemini..."):
            prompt_testo = (
                f"Agisci come un analista finanziario esperto in criptovalute. "
                f"Analizza la criptovaluta {crypto_symbol} che quota attualmente ${current_price}. "
                f"Il trader adotta uno stile di {trading_style} con un profilo di rischio {risk_level}. "
                f"Fornisci un'indicazione chiara (BUY, SELL o HOLD), i livelli chiave di supporto/resistenza stimati "
                f"e una motivazione tecnica dettagliata."
            )
            
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt_testo,
                )
                
                st.subheader("🤖 Risultato Analisi IA")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"❌ Errore durante la generazione della risposta: {e}")
else:
    st.info("👈 Seleziona la crypto e i parametri dalla barra laterale, quindi clicca su **Genera Analisi Avanzata**.")
