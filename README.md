# Crypto Signal Lab 🚀 – Free Multi Agent

Dashboard multi-agente **completamente gratuita** per analisi crypto con dati on-chain e social sentiment.

## Funzionalità

- **Multi-Agente a scelta** (attivi solo provider free):
  - Gemini – Analista Generale
  - Gemini – Analista Tecnico
  - Gemini – On-Chain & Risk
  - Groq – Analista Veloce
  - Groq – Sentiment & Macro
- **Agente Sintetizzatore finale** (Gemini) → produce un unico verdetto operativo
- Prezzi e volume 24h da **Binance**
- TVL delle chain da **DefiLlama** (free)
- Dati on-chain Bitcoin da **mempool.space** (fee, mempool, difficulty)
- **Social Sentiment**: Crypto Fear & Greed Index (alternative.me)
- Profilo trading personalizzabile (Day / Swing / HODL + rischio)

## API Key gratuite necessarie

| Provider | Dove ottenerla | Costo |
|----------|----------------|-------|
| **Gemini** | [aistudio.google.com](https://aistudio.google.com) | Gratis |
| **Groq** | [console.groq.com](https://console.groq.com) | Gratis |

> Entrambe le key si ottengono senza carta di credito.

## Deploy su Streamlit Community Cloud

1. Vai su [share.streamlit.io](https://share.streamlit.io)
2. Collega questo repository
3. Imposta i **Secrets**:

```toml
GEMINI_API_KEY = "la-tua-key-gemini"
GROQ_API_KEY = "la-tua-key-groq"