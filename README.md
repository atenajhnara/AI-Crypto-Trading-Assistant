# 🤖 Smart Crypto Trading Assistant | دستیار هوشمند ترید کریپتو

A Python script that acts like a professional crypto trader, analyzing candlestick data and key technical indicators (MA50, MA200, RSI, MACD) to generate simple BUY / SELL / WAIT signals for BTC/USDT on Bybit Futures.

یک اسکریپت پایتون که مانند یک تریدر حرفه‌ای با داده‌های کندل و اندیکاتورهای مهم (MA50، MA200، RSI و MACD) کار می‌کند و سیگنال‌های ساده خرید، فروش یا انتظار برای BTC/USDT در Bybit Futures تولید می‌کند.

---

## 🧠 Technologies Used | تکنولوژی‌های استفاده‌شده

- Python 3.10+  
- pybit (دریافت داده از Bybit Futures)  
- pandas / numpy (پردازش داده)  

---

## ⚙️ How It Works | نحوه کار

1. Connect to Bybit Futures API and fetch candlestick data.  
   اتصال به Bybit Futures API و دریافت داده‌های کندل.

2. Compute technical indicators:  
   محاسبه اندیکاتورهای تکنیکال:  
   - MA50 & MA200  
   - RSI  
   - MACD & Signal Line  

3. Generate trading signals based on indicator conditions:  
   تولید سیگنال‌های ترید بر اساس شرایط اندیکاتورها:  
   - BUY  
   - SELL  
   - WAIT  

4. Display latest signals with indicator values in the terminal.  
   نمایش آخرین سیگنال‌ها همراه با مقادیر اندیکاتورها در ترمینال.

---

## 🧩 Key Code Structure | ساختار اصلی کد

```python
# Connect to Bybit Futures
session = HTTP("https://api.bybit.com")
data = session.get_kline(category="linear", symbol="BTCUSDT", interval="60", limit=500)
df = pd.DataFrame(data['result'])

# Convert columns
df['timestamp'] = pd.to_datetime(df['open_time'], unit='s')
df['close'] = df['close'].astype(float)

# Compute indicators
df['MA50'] = df['close'].rolling(50).mean()
df['MA200'] = df['close'].rolling(200).mean()

def compute_RSI(series, period=14):
    delta = series.diff()
    gain = delta.where(delta>0,0)
    loss = -delta.where(delta<0,0)
    RSI = 100 - (100/(1 + gain.rolling(period).mean()/loss.rolling(period).mean()))
    return RSI

df['RSI'] = compute_RSI(df['close'])

# MACD & Signal
def compute_MACD(series):
    EMAfast = series.ewm(span=12, adjust=False).mean()
    EMAslow = series.ewm(span=26, adjust=False).mean()
    MACD = EMAfast - EMAslow
    Signal = MACD.ewm(span=9, adjust=False).mean()
    return MACD, Signal

df['MACD'], df['Signal'] = compute_MACD(df['close'])

# Generate trading signal
def generate_signal(row):
    if row['MA50'] > row['MA200'] and row['RSI'] > 30 and row['MACD'] > -50:
        return 'BUY'
    elif row['MA50'] < row['MA200'] or row['RSI'] < 35:
        return 'SELL'
    return 'WAIT'

df['Signal_Type'] = df.apply(generate_signal, axis=1)

print(df[['timestamp','close','MA50','MA200','RSI','MACD','Signal_Type']].tail(10))
