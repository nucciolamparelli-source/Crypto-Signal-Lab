import os
import streamlit as st
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(
    page_title="Crypto Signal Lab – Free Multi Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== SIDEBAR ======================
st.sidebar.title("⚙️ Configurazione Free")

gemini_key = os.getenv("GEMINI_API_KEY") or st.sidebar.text_input(
    "Gemini API Key (free)", type="password",
    help="Gratis su aistudio.google.com"
)
groq_key = os.getenv("GROQ_API_KEY") or st.sidebar.text_input(
    "Groq API Key (free)", type="password",
    help="Gratis su console.groq.com"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Seleziona gli Agenti Free")

agent_options = {
    "Gemini – Analista Generale": "gemini_general",
    "Gemini – Analista Tecnico": "gemini_tech",
    "Gemini – On-Chain & Risk": "gemini_risk",
    "Groq – Analista Veloce": "groq_fast",
    "Groq – Sentiment & Macro": "groq_macro",
}

selected_agents = st.sidebar.multiselect(
    "Quali agenti vuoi attivare?",
    options=list(agent_options.keys()),
    default=["Gemini – Analista Generale", "Gemini – Analista Tecnico", "Groq – Sentiment & Macro"]
)

enable_synthesizer = st.sidebar.checkbox("Attiva Agente Sintetizzatore finale (Gemini)", value=True)

st.sidebar.markdown("---")

CRYPTO_MAP = {
    "BTCUSDT": {"name": "Bitcoin", "symbol": "BTC", "chain": "Bitcoin"},
    "ETHUSDT": {"name": "Ethereum", "symbol": "ETH", "chain": "Ethereum"},
    "SOLUSDT": {"name": "Solana", "symbol": "SOL", "chain": "Solana"},
    "BNBUSDT": {"name": "BNB", "symbol": "BNB", "chain": "BSC"},
    "XRPUSDT": {"name": "XRP", "symbol": "XRP", "chain": "Ripple"},
    "ADAUSDT": {"name": "Cardano", "symbol": "ADA", "chain": "Cardano"},
    "DOGEUSDT": {"name": "Dogecoin", "symbol": "DOGE", "chain": "Dogecoin"},
    "AVAXUSDT": {"name": "Avalanche", "symbol": "AVAX", "chain": "Avalanche"},
}

crypto_symbol = st.sidebar.selectbox(
    "Seleziona Crypto",
    list(CRYPTO_MAP.keys()),
    format_func=lambda x: f"{CRYPTO_MAP[x]['name']} ({x})"
)
trading_style = st.sidebar.selectbox(
    "Stile di Trading",
    ["Day Trading (Breve termine)", "Swing Trading (Medio termine)", "HODL / Investimento (Lungo termine)"]
)
risk_level = st.sidebar.selectbox(
    "Profilo di Rischio",
    ["Conservativo", "Bilanciato", "Aggressivo"]
)

analyze_button = st.sidebar.button("🚀 Lancia Multi-Agente Free", type="primary", use_container_width=True)

# ====================== DATA FUNCTIONS ======================
@st.cache_data(ttl=60)
def get_binance_price(symbol: str):
    # Prima prova Binance
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=10)
        r.raise_for_status()
        data = r.json()
        return {
            "price": float(data["lastPrice"]),
            "change_24h": float(data["priceChangePercent"]),
            "high_24h": float(data["highPrice"]),
            "low_24h": float(data["lowPrice"]),
            "volume": float(data["quoteVolume"]),
        }
    except Exception:
        pass

    # Fallback su CoinGecko (gratuito)
    try:
        # Mappa simbolo Binance → id CoinGecko
        coingecko_map = {
            "BTCUSDT": "bitcoin",
            "ETHUSDT": "ethereum",
            "SOLUSDT": "solana",
            "BNBUSDT": "binancecoin",
            "XRPUSDT": "ripple",
            "ADAUSDT": "cardano",
            "DOGEUSDT": "dogecoin",
            "AVAXUSDT": "avalanche-2",
        }
        coin_id = coingecko_map.get(symbol)
        if not coin_id:
            return None

        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        market = data["market_data"]
        return {
            "price": float(market["current_price"]["usd"]),
            "change_24h": float(market["price_change_percentage_24h"] or 0),
            "high_24h": float(market["high_24h"]["usd"]),
            "low_24h": float(market["low_24h"]["usd"]),
            "volume": float(market["total_volume"]["usd"]),
        }
    except Exception:
        return None
        

@st.cache_data(ttl=300)
def get_defillama_tvl(chain_name: str):
    try:
        r = requests.get("https://api.llama.fi/v2/chains", timeout=10)
        r.raise_for_status()
        for c in r.json():
            if c.get("name", "").lower() == chain_name.lower() or c.get("tokenSymbol", "").upper() == chain_name.upper():
                return {"tvl": c.get("tvl"), "name": c.get("name")}
        return None
    except Exception:
        return None

@st.cache_data(ttl=120)
def get_btc_onchain():
    try:
        fees = requests.get("https://mempool.space/api/v1/fees/recommended", timeout=8).json()
        mempool = requests.get("https://mempool.space/api/mempool", timeout=8).json()
        difficulty = requests.get("https://mempool.space/api/v1/difficulty-adjustment", timeout=8).json()
        return {
            "fastest_fee": fees.get("fastestFee"),
            "half_hour_fee": fees.get("halfHourFee"),
            "hour_fee": fees.get("hourFee"),
            "mempool_tx_count": mempool.get("count"),
            "mempool_vsize": mempool.get("vsize"),
            "difficulty_change": difficulty.get("difficultyChange"),
            "progress_percent": difficulty.get("progressPercent"),
            "remaining_blocks": difficulty.get("remainingBlocks"),
        }
    except Exception:
        return None

@st.cache_data(ttl=300)
def get_fear_greed_index():
    """Crypto Fear & Greed Index - free, no key needed"""
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=8)
        r.raise_for_status()
        data = r.json()["data"][0]
        value = int(data["value"])
        classification = data["value_classification"]
        return {
            "value": value,
            "classification": classification,
            "timestamp": data["timestamp"]
        }
    except Exception:
        return None

def interpret_sentiment(fg):
    if not fg:
        return "Sentiment non disponibile"
    v = fg["value"]
    if v <= 25:
        return "Extreme Fear – possibile opportunità di accumulo, ma attenzione al rischio di ulteriori ribassi"
    elif v <= 45:
        return "Fear – mercato cauto, buona zona per valutazioni selettive"
    elif v <= 55:
        return "Neutral – mercato indeciso"
    elif v <= 75:
        return "Greed – euforia crescente, attenzione a correzioni"
    else:
        return "Extreme Greed – rischio elevato di presa di profitto / correzione"

# ====================== AGENT SYSTEM ======================
def build_base_context(info, price_data, tvl_data, btc_onchain, fg_data, trading_style, risk_level):
    onchain_ctx = ""
    if tvl_data and tvl_data.get("tvl"):
        onchain_ctx += f"- TVL {info['chain']}: ${tvl_data['tvl']:,.0f}\n"
    if btc_onchain:
        onchain_ctx += (
            f"- Fee BTC: fastest {btc_onchain.get('fastest_fee')} sat/vB | "
            f"mempool {btc_onchain.get('mempool_tx_count'):,} tx\n"
            f"- Difficulty change: {btc_onchain.get('difficulty_change', 0):+.2f}%\n"
        )

    sentiment_ctx = ""
    if fg_data:
        sentiment_ctx = (
            f"- Fear & Greed Index: {fg_data['value']}/100 ({fg_data['classification']})\n"
            f"- Interpretazione: {interpret_sentiment(fg_data)}\n"
        )

    return f"""
Asset: {info['name']} ({crypto_symbol})
Prezzo: ${price_data['price']:,.2f} | 24h: {price_data['change_24h']:+.2f}%
High/Low 24h: ${price_data['high_24h']:,.2f} / ${price_data['low_24h']:,.2f}
Volume 24h: ${price_data['volume']:,.0f}

On-chain:
{onchain_ctx if onchain_ctx else "Dati on-chain limitati"}

Social Sentiment:
{sentiment_ctx if sentiment_ctx else "Sentiment non disponibile"}

Trader: stile {trading_style} | rischio {risk_level}
"""

AGENT_SYSTEMS = {
    "gemini_general": {
        "provider": "gemini",
        "system": "Sei un analista crypto esperto, bilanciato e basato sui dati. Rispondi in italiano. Dai un segnale chiaro BUY/SELL/HOLD con confidenza e motivazione sintetica.",
        "focus": "Analisi generale bilanciata (prezzo + on-chain + sentiment)."
    },
    "gemini_tech": {
        "provider": "gemini",
        "system": "Sei un analista tecnico puro. Concentrati su struttura del prezzo, supporti/resistenze, momentum e timeframe. Dai livelli operativi chiari. Rispondi in italiano.",
        "focus": "Analisi tecnica e livelli chiave."
    },
    "gemini_risk": {
        "provider": "gemini",
        "system": "Sei un Risk Manager e On-Chain Specialist. Evidenzia rischi, scenari negativi, fee, mempool, TVL e livelli di invalidazione. Sii prudente. Rispondi in italiano.",
        "focus": "Rischio + dati on-chain."
    },
    "groq_fast": {
        "provider": "groq",
        "system": "Sei un analista crypto veloce e diretto. Vai dritto al punto: segnale, confidenza, livelli e motivazione breve. Rispondi in italiano.",
        "focus": "Analisi rapida e operativa."
    },
    "groq_macro": {
        "provider": "groq",
        "system": "Sei un analista di sentiment e macro. Usa il Fear & Greed Index e il contesto di mercato per valutare euforia o paura. Rispondi in italiano.",
        "focus": "Sentiment sociale e macro."
    },
}

def call_gemini(system: str, user_prompt: str, api_key: str) -> str:
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        full_prompt = f"{system}\n\n{user_prompt}"
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=full_prompt,
        )
        return response.text
    except Exception as e:
        return f"❌ Errore Gemini: {e}"

def call_groq(system: str, user_prompt: str, api_key: str) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.35,
            max_tokens=900,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Errore Groq: {e}"

def run_agent(agent_key: str, context: str, gemini_key: str, groq_key: str) -> tuple[str, str]:
    cfg = AGENT_SYSTEMS[agent_key]
    user_prompt = f"{context}\n\nFocus richiesto: {cfg['focus']}\n\nFornisci: segnale (BUY/SELL/HOLD), confidenza, livelli chiave, motivazione breve e rischi."

    if cfg["provider"] == "gemini":
        if not gemini_key:
            return agent_key, "⚠️ GEMINI_API_KEY mancante"
        return agent_key, call_gemini(cfg["system"], user_prompt, gemini_key)
    else:
        if not groq_key:
            return agent_key, "⚠️ GROQ_API_KEY mancante"
        return agent_key, call_groq(cfg["system"], user_prompt, groq_key)

def run_synthesizer(context: str, agent_results: dict, gemini_key: str) -> str:
    if not gemini_key:
        return "⚠️ GEMINI_API_KEY mancante – impossibile eseguire il Sintetizzatore."

    opinions = ""
    for name, key in agent_options.items():
        if key in agent_results:
            opinions += f"\n### {name}\n{agent_results[key]}\n"

    system = (
        "Sei l'Agente Sintetizzatore finale. Hai ricevuto i pareri di diversi analisti free. "
        "Produci un UNICO verdetto operativo chiaro. Sii diretto e actionable. Rispondi in italiano."
    )

    user_prompt = f"""
Contesto di mercato:
{context}

Pareri degli agenti:
{opinions}

---
PRODUCI IL VERDETTO FINALE con questa struttura:

1. **Segnale Finale**: BUY / SELL / HOLD
2. **Confidenza**: Bassa / Media / Alta
3. **Livelli Chiave**: Entrata – Stop Loss – Take Profit
4. **Sintesi motivazionale** (max 6-7 righe) che tiene conto anche del sentiment
5. **Rischi principali**
6. **Nota sulla divergenza** (se presente)
"""
    return call_gemini(system, user_prompt, gemini_key)

# ====================== UI ======================
st.title("🚀 Crypto Signal Lab – Free Multi Agent")
st.caption("Solo agenti gratuiti • Gemini + Groq • On-chain + Social Sentiment • Sintetizzatore")

info = CRYPTO_MAP[crypto_symbol]
price_data = get_binance_price(crypto_symbol)
fg_data = get_fear_greed_index()

# Metrics
c1, c2, c3, c4 = st.columns(4)
if price_data:
    c1.metric(f"{info['name']}", f"${price_data['price']:,.2f}", f"{price_data['change_24h']:+.2f}%")
    c2.metric("24h High", f"${price_data['high_24h']:,.2f}")
    c3.metric("24h Low", f"${price_data['low_24h']:,.2f}")
    vol = price_data["volume"]
    c4.metric("Volume 24h", f"${vol/1e9:.2f}B" if vol > 1e9 else f"${vol/1e6:.1f}M")
else:
    st.warning("Prezzo non disponibile")

st.markdown("---")

# Sentiment + On-chain
st.subheader("📡 On-Chain + Social Sentiment")

col_a, col_b, col_c, col_d = st.columns(4)

tvl_data = get_defillama_tvl(info["chain"])
btc_onchain = get_btc_onchain() if crypto_symbol == "BTCUSDT" else None

with col_a:
    if tvl_data and tvl_data.get("tvl"):
        tvl = tvl_data["tvl"]
        st.metric(f"TVL {info['chain']}", f"${tvl/1e9:.2f}B" if tvl > 1e9 else f"${tvl/1e6:.1f}M")
    else:
        st.metric(f"TVL {info['chain']}", "N/D")

with col_b:
    if fg_data:
        st.metric("Fear & Greed", f"{fg_data['value']}/100", fg_data["classification"])
    else:
        st.metric("Fear & Greed", "N/D")

with col_c:
    if btc_onchain:
        st.metric("Fee più veloce", f"{btc_onchain.get('fastest_fee')} sat/vB")
    else:
        st.metric("Fee BTC", "Solo per BTC")

with col_d:
    if btc_onchain:
        st.metric("Tx in Mempool", f"{btc_onchain.get('mempool_tx_count', 0):,}")
    else:
        st.caption("Fonte sentiment: alternative.me")

if fg_data:
    st.info(f"**Interpretazione Sentiment:** {interpret_sentiment(fg_data)}")

st.markdown("---")

# ====================== RUN ======================
if analyze_button:
    if not selected_agents:
        st.warning("Seleziona almeno un agente.")
        st.stop()
    if not price_data:
        st.error("Impossibile recuperare i dati di mercato.")
        st.stop()

    context = build_base_context(info, price_data, tvl_data, btc_onchain, fg_data, trading_style, risk_level)
    agent_keys = [agent_options[name] for name in selected_agents]

    st.subheader(f"🤖 Panel Multi-Agente Free ({len(agent_keys)} attivi)")

    results = {}
    progress = st.progress(0, text="Gli agenti free stanno lavorando...")

    with ThreadPoolExecutor(max_workers=min(5, len(agent_keys))) as executor:
        futures = {
            executor.submit(run_agent, key, context, gemini_key, groq_key): key
            for key in agent_keys
        }
        done = 0
        for future in as_completed(futures):
            key, output = future.result()
            results[key] = output
            done += 1
            progress.progress(done / len(agent_keys), text=f"Completati {done}/{len(agent_keys)}")

    progress.empty()

    for name in selected_agents:
        key = agent_options[name]
        with st.expander(f"**{name}**", expanded=False):
            st.markdown(results.get(key, "Nessun risultato"))

    if enable_synthesizer:
        st.markdown("---")
        st.subheader("🧠 Agente Sintetizzatore – Verdetto Finale")

        with st.spinner("Il Sintetizzatore sta preparando il verdetto..."):
            final_verdict = run_synthesizer(context, results, gemini_key)

        st.success("Verdetto generato")
        st.markdown(final_verdict)
    else:
        st.info("Sintetizzatore disattivato.")

else:
    st.info("👈 Scegli gli agenti e clicca **Lancia Multi-Agente Free**")

st.markdown("---")
st.caption(f"Crypto Signal Lab – Free Agents + Social Sentiment • {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC • Non è consulenza finanziaria")