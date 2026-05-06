# AI Destekli Binance TR Kripto Sinyal Botu

Binance TR uzerindeki aktif TRY paritelerini tarar, hacim ve fiyat kriterlerine gore en yuksek puanli 3 firsati Telegram'a yollar.

> Bu proje al-sat emri vermez. Sadece karar destek ve sinyal uretim sistemi olarak tasarlanmistir.

## Ozellikler

- Binance TR REST API v3 public market data
- Tum aktif TRY paritelerini dinamik cekme
- Dusuk likiditeli coinleri eleme
- 8 puanlik skor sistemi
- Ilk 3 firsati raporlama
- Hedef satis ve stop-loss hesaplama
- Ayni sinyali belirli sure tekrar gondermeme
- Telegram Bot API bildirimi
- GitHub Actions ile 15 dakikada bir calisma

## Kurulum

```bash
cp .env.example .env
pip install -r requirements.txt
python -m crypto_signal_bot.main
```

## GitHub Secrets

GitHub repo ayarlarindan su secrets degerlerini ekle:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Opsiyonel:

- `MIN_VOLUME_TRY`
- `HIGH_VOLUME_TRY`
- `SIGNAL_COOLDOWN_HOURS`

## GitHub Actions

Workflow dosyasi `.github/workflows/signal-bot.yml` icindedir. Her 15 dakikada bir calisir.

## Notlar

- API key gerekmez; sadece public Binance TR market data kullanir.
- Emir verme, bakiye okuma veya otomatik trade yoktur.
- Hedef satis varsayilan olarak +18%, stop-loss -5% hesaplanir.
