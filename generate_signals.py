import pyupbit
import pandas as pd
import json
import os
import requests

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Load price data
df = pyupbit.get_ohlcv("KRW-BTC", interval="minute240", count=200)
df["EMA20"] = df["close"].ewm(span=20).mean()
df["EMA50"] = df["close"].ewm(span=50).mean()
df["RSI"] = compute_rsi(df["close"])

def check_condition(prev, current):
    return (
        current["EMA20"] > current["EMA50"]
        and prev["close"] < prev["EMA20"]
        and current["close"] > current["EMA20"]
        and current["RSI"] > 45
    )

# Check for current signals
current = []
if True: 
    signal = {
        "strategy": "EMA 눌림목",
        "symbol": "BTC",
        "price": int(df.iloc[-1]["close"]),
        "rsi": round(df.iloc[-1]["RSI"], 2),
        "time": df.index[-1].strftime("%Y-%m-%d %H:%M")
    }
    current.append(signal)

    # Telegram alert
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        text = f"📢 시그널 발생!\n{signal['strategy']}\n시간: {signal['time']}\n가격: ₩{signal['price']:,}\nRSI: {signal['rsi']}"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": text})

# History signals
history = []
for i in range(1, len(df) - 1):
    if check_condition(df.iloc[i - 1], df.iloc[i]):
        history.append({
            "strategy": "EMA 눌림목",
            "symbol": "BTC",
            "price": int(df.iloc[i]["close"]),
            "rsi": round(df.iloc[i]["RSI"], 2),
            "time": df.index[i].strftime("%Y-%m-%d %H:%M")
        })

history = history[-5:]

# Save to JSON
signals = {
    "current": current,
    "history": history
}

with open("docs/signals.json", "w", encoding="utf-8") as f:
    json.dump(signals, f, ensure_ascii=False, indent=2)

print(f"✅ 시그널 생성 완료: current {len(current)}개, history {len(history)}개")
