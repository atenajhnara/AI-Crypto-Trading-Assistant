#یه دستیار بسازیم که بتونه مثل یه تریدر حرفه‌ای باهات حرف بزنه، چارت و اندیکاتورها رو تحلیل کنه، و بگه الان بازار در چه وضعیه (مثلاً لانگ یا شورت منطقیه یا نه)



from pybit.v5.http import HTTP
import pandas as pd
import numpy as np

# ----------- اتصال به Bybit فیوچرز -----------
session = HTTP("https://api.bybit.com")

symbol = "BTCUSDT"
interval = "60"  # 60 دقیقه
limit = 500       # تعداد کندل برای MA200

# گرفتن داده کندل
data = session.get_kline(category="linear", symbol=symbol, interval=interval, limit=limit)
df = pd.DataFrame(data['result'])

# ادامه کد همانند قبل ...

# ----------- تبدیل ستون‌ها -----------
df['timestamp'] = pd.to_datetime(df['open_time'], unit='s')
df['close'] = df['close'].astype(float)
df['open'] = df['open'].astype(float)
df['high'] = df['high'].astype(float)
df['low'] = df['low'].astype(float)

# ----------- محاسبه اندیکاتورها -----------

# MA50 و MA200
df['MA50'] = df['close'].rolling(50).mean()
df['MA200'] = df['close'].rolling(200).mean()

# RSI
def compute_RSI(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    RS = avg_gain / avg_loss
    RSI = 100 - (100 / (1 + RS))
    return RSI

df['RSI'] = compute_RSI(df['close'], 14)

# MACD و خط سیگنال
def compute_MACD(series, fast=12, slow=26, signal=9):
    EMAfast = series.ewm(span=fast, adjust=False).mean()
    EMAslow = series.ewm(span=slow, adjust=False).mean()
    MACD = EMAfast - EMAslow
    Signal = MACD.ewm(span=signal, adjust=False).mean()
    return MACD, Signal

df['MACD'], df['Signal'] = compute_MACD(df['close'])

# ----------- تابع تولید سیگنال -----------
def generate_signal(row):
    if pd.isna(row['MA50']) or pd.isna(row['MA200']) or pd.isna(row['RSI']) or pd.isna(row['MACD']) or pd.isna(row['Signal']):
        return 'WAIT'
    
    # شرط BUY
    if (row['MA50'] > row['MA200']) and (row['RSI'] > 30) and (row['MACD'] > -50):
        return 'BUY'
    
    # شرط SELL نرم
    if (row['MA50'] < row['MA200']) or (row['RSI'] < 35) or (row['MACD'] < -50):
        return 'SELL'
    
    return 'WAIT'

df['Signal_Type'] = df.apply(generate_signal, axis=1)

# ----------- نمایش چند ردیف آخر -----------
print(df[['timestamp','close','MA50','MA200','RSI','MACD','Signal','Signal_Type']].tail(20))