
from datetime import datetime, timedelta,timezone
import time
import uuid

import pandas as pd

from bitget.exceptions import BitgetAPIException


# 익절가 계산 함수 (추세매매 시 사용)
def calc_target_price(entry_price, leverage, target_profit_ratio):
    # target_profit_ratio 예: 0.2 = 20%
    price_change_ratio = target_profit_ratio / leverage
    return entry_price * (1 + price_change_ratio)



if __name__ == '__main__':
    
    client_oid = str(uuid.uuid4())
    
    
    params = {
    "symbol": "BTCUSDT",
    "marginCoin": "USDT",
    "productType": "susdt-futures",
    "leverage": 50,
    }
    # baseApi.post('/api/v2/mix/account/set-leverage',params)
    
    try:



        # 주문 예시
        params = {
        "symbol": "BTCUSDT",
        "productType": "susdt-futures",
        "marginMode": "isolated",  # "cross" or "isolated"
        "marginCoin": "USDT",
        "size": "0.1",
        "side": "buy", # "buy" or "sell"
        "tradeSide": "open", # "open" or "close"
        "orderType": "limit", # "limit" or "market"
        "price":90000, # 마켓일때는 필요없음
        "force": "gtc",
        "clientOid": client_oid, # UUID로 생성된 고유한 주문 ID 옵션
        "reduceOnly": "NO",
        # "presetStopSurplusPrice": "", #익절가 설정
        # "presetStopLossPrice":"" , #손절가 설정
        }
        
        

        
        # 주문 실행
        # response = maxOrderApi.placeOrder(params)
        
        
    except BitgetAPIException as e:
        print("1 error:" + e.message)
        
    # 주문 상세 보기
    # maxOrderApi.detail({"symbol": "BTCUSDT", "productType": "SUSDT-FUTURES", "orderId":"1315675579978186753"}) 
       
    # 대기중 주문 보기
    # maxOrderApi.ordersPending({"symbol": "BTCUSDT", "productType": "SUSDT-FUTURES", })    
    
    # 주문 취소
    # maxOrderApi.cancelOrder({"symbol": "BTCUSDT",  "productType": "SUSDT-FUTURES","orderId":"1315675579978186753"})
    

   
    
    # try:
    #     params= {}
    #     params["productType"] = "SUSDT-FUTURES"
    #     response = marketApi.tickers(params)
        
    # except BitgetAPIException as e:
    #     print("t error:" + e.message)

        
    # try:
    #     params = {}
    #     params["productType"] = "susdt-futures"
    #     params['symbol'] = "SBTCSUSDT"
        
        
    #     response = marketApi.contracts(params)
    # except BitgetAPIException as e:
    #     print("2 error:" + e.message)


    # # Demo 4:send get request with no params
    # try:
    #     params = {}
    #     response = baseApi.get("/api/v2/mix/account/account", params)
    #     print(response)
    # except BitgetAPIException as e:
    #     print("3 error:" + e.message)

    
    
   

