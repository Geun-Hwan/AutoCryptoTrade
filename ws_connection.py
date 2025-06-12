#!/usr/bin/python
from datetime import datetime, timedelta, timezone
import json
import time

from backtesting import TradingBacktest
from bitget.ws.bitget_ws_client import  SubscribeReq

from bitget_helpers import get_ws_client
candles = []

MAX_CANDLES = 3000  # 최대 캔들 수
candle_columns = ["timestamp", "open", "high", "low", "close", "volume", "quote_volume"]

def format_timestamp(ms_timestamp):
    dt = datetime.fromtimestamp(int(ms_timestamp) / 1000, tz=timezone.utc)
    return (dt + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')


def print_ticker(data):
    ticker = data[0]  # 한 종목 기준
    print("\n📊 실시간 티커 정보 (BTCUSDT)")
    print(f"🕒 시각: {format_timestamp(ticker['ts'])}")
    print(f"📈 현재가: {ticker['lastPr']}")
    print(f"📉 24H 최저가: {ticker['low24h']}")
    print(f"📊 24H 최고가: {ticker['high24h']}")
    print(f"🔁 24H 등락률: {float(ticker['change24h']) * 100:.2f}%")
    print(f"💰 매수호가: {ticker['bidPr']} ({ticker['bidSz']} BTC)")
    print(f"💰 매도호가: {ticker['askPr']} ({ticker['askSz']} BTC)")
    print(f"📦 거래량: {ticker['baseVolume']} BTC / {float(ticker['quoteVolume']):,.0f} USD")
    print(f"💵 마크가격: {ticker['markPrice']} | 지수가격: {ticker['indexPrice']}")
    print(f"📆 다음 펀딩시각: {format_timestamp(ticker['nextFundingTime'])}")
    

            
def handle(message):
    try:
        response = json.loads(message)

        data = response.get("data", [])
        if not data:
            print("No data.")
            return

        # print("\n📈 실시간 티커 데이터:")
        # print_ticker(data)
       
    except Exception as e:
        print("❌ Error handling message:", e)


    

def _parse_candle(raw):
    parsed = dict(zip(candle_columns, raw))
    parsed["timestamp"] = format_timestamp(parsed["timestamp"])
    
    # print(
    #             f"{parsed['timestamp']} | O: {parsed['open']} H: {parsed['high']} "
    #             f"L: {parsed['low']} C: {parsed['close']} V: {parsed['volume']}"
    #         )
    return parsed

def _update_candles(candles, new_candle):
    if not candles:
        candles.append(new_candle)
        return

    if candles[-1]["timestamp"] == new_candle["timestamp"]:
        candles[-1] = new_candle  # 최신 봉이면 교체
    else:
        candles.append(new_candle)

    if len(candles) > MAX_CANDLES:
        candles.pop(0)


def handle_candle(message_str):
    global candles

    try:
        response = json.loads(message_str)
        action = response.get("action")
        data = response.get("data", [])

        if not data:
            return

        if action == "snapshot":
            print(f"\n📦 snapshot 수신 - {len(data)}개 캔들")
            candles = [_parse_candle(c) for c in data][-MAX_CANDLES:]
            
                        

        elif action == "update":
            print(f"\n📡 실시간 update")
            for raw in data:
                print(data)
                _update_candles(candles, _parse_candle(raw))


            
    except Exception as e:
        print("❌ Error handling candle message:", e)
        
    



if __name__ == '__main__':

        

    wsClient =get_ws_client()
    
    #  실시간 티커 정보(가격 변동 등)
    channles = [SubscribeReq("USDT-FUTURES", "ticker", "BTCUSDT"),]
    wsClient.subscribe(channles, handle)
    
    # 5분봉 캔들 정보 (초기 500개 , 이후 실시간 업데이트)
    channles = [SubscribeReq("USDT-FUTURES", "candle5m", "BTCUSDT")]
    wsClient.subscribe(channles, handle_candle)
    
    
