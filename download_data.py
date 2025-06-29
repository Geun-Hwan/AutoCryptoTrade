from datetime import datetime, timedelta, timezone
import time

import pandas as pd

from bitget_helpers import  marketApi



def fetch_candles_by_date(start_date, end_date, symbol="BTCUSDT", product_type="usdt-futures", granularity="5m"):
    all_data = []
    current_date = start_date

    while current_date < end_date:
        start_ts = int(current_date.timestamp() * 1000)  # 밀리초
        end_ts = int((current_date + timedelta(days=1)).timestamp() * 1000)  # 다음날 밀리초

        params = {
            "symbol": symbol,
            "productType": product_type,
            "granularity": granularity,
            "startTime": start_ts,
            "endTime": end_ts,
            "kLineType": "market",
            "limit": 1000,
        }

        response = marketApi.candles(params)
        data = response.get('data', [])

        if data:
            all_data.extend(data)
        else:
            print(f"No data for {current_date.strftime('%Y-%m-%d')}")

        current_date += timedelta(days=1)
        time.sleep(0.2)  # API 호출 간 딜레이 (필요에 따라 조절)

    # 데이터 프레임 변환
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
    df = pd.DataFrame(all_data, columns=columns)

    # 타입 변환 및 타임존 변환
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul').dt.strftime('%Y-%m-%d %H:%M:%S')


    for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
        df[col] = df[col].astype(float)

    return df


if __name__ == "__main__":
    
    start_date = datetime(2025, 6, 11)
    end_date = datetime(2025, 6, 29)  
    
    
    df = fetch_candles_by_date(start_date, end_date)
    df.to_csv('./data/bit_candles_20250611_to_20250629.csv', index=False)
    # df = fetch_candles_by_date(start_date, end_date ,symbol="ETCUSDT")
    # df.to_csv('eth_candles_20250511_to_20250610.csv', index=False)
    