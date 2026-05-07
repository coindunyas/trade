# 🚀 AI Crypto Signal Bot

AI destekli kripto sinyal sistemi.

Bu sistem CoinGecko üzerinden TRY bazlı kripto verilerini çeker, coinleri skorlar ve Telegram üzerinden sinyal gönderir.

---

# Özellikler

- TRY bazlı coin tarama
- 8 puanlık AI skor sistemi
- İlk 3 fırsatı seçme
- Telegram bildirimi
- Alış bölgesi
- Satış 1 ve Satış 2
- Stop-loss
- Risk seviyesi
- GitHub Actions ile 15 dakikada bir otomatik çalışma
- Streamlit dashboard

---

# Kurulum

```bash
pip install -r requirements.txt
python main.py
```

---

# Dashboard

```bash
streamlit run dashboard.py
```

---

# GitHub Secrets

Repo ayarlarından şunları ekle:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

---

# GitHub Actions

Workflow dosyası:

```text
.github/workflows/signal-bot.yml
```

Sistem her 15 dakikada bir otomatik çalışır.

---

# Telegram Mesaj Formatı

```text
🚀 EN VERİMLİ 3 FIRSAT

#BTCTRY (Skor: 7/8)

💰 Fiyat
🟢 Alış Bölgesi
🎯 Satış 1
🚀 Satış 2
🛑 Stop-Loss
⚠️ Risk
📊 Hacim
🧠 Sebep
```

---

# Kademeli Satış Mantığı

- Satış 1: %10 kar hedefi, pozisyonun %50'si
- Satış 2: %18 kar hedefi, kalan %50
- Stop-loss: %5 zarar kes

---

# Dashboard Deploy

Streamlit Cloud:

```text
https://share.streamlit.io
```

GitHub repo bağla, ana dosya olarak:

```text
dashboard.py
```

seç ve deploy et.

---

# Uyarı

Bu sistem yatırım tavsiyesi değildir.  
Sadece karar destek amacıyla kullanılır.
