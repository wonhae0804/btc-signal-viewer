# 전략 시그널 생성기 (EMA + VPVR)
import pyupbit
import pandas as pd
import json
from datetime import datetime

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df = pyupbit.get_ohlcv("KRW-BTC", interval="minute240", count=200)
df["EMA20"] = df["close"].ewm(span=20).mean()
df["EMA50"] = df["close"].ewm(span=50).mean()
df["RSI"] = compute_rsi(df["close"])

signals = []
now = datetime.now().strftime("%Y-%m-%d %H:%M")
last = df.iloc[-1]
prev = df.iloc[-2]

if last["EMA20"] > last["EMA50"] and prev["close"] < prev["EMA20"] and last["close"] > last["EMA20"] and last["RSI"] > 45:
    signals.append({
        "strategy": "EMA 눌림목",
        "symbol": "BTC",
        "price": int(last["close"]),
        "rsi": round(last["RSI"], 2),
        "time": now
    })

poc = df["close"].round(-3).value_counts().idxmax()
if abs(last["close"] - poc) / poc < 0.01 and last["RSI"] > 45:
    signals.append({
        "strategy": "VPVR 유사",
        "symbol": "BTC",
        "price": int(last["close"]),
        "rsi": round(last["RSI"], 2),
        "time": now
    })

with open("docs/signals.json", "w", encoding="utf-8") as f:
    json.dump(signals, f, ensure_ascii=False, indent=2)

print(f"{len(signals)}개의 시그널 생성됨.")
