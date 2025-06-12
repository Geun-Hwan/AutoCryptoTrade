from bitget import consts as c




import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

from bitget.v2.mix import account_api
from bitget.v2.mix.account_api import AccountApi
from bitget.v2.mix.market_api import MarketApi
from bitget.v2.mix.order_api import OrderApi
from bitget.bitget_api import BitgetApi

from bitget.ws.bitget_ws_client import BitgetWsClient

load_dotenv()

is_demo = os.getenv("BITGET_DEMO_MODE", "0") == "1"



api_key = quote_plus(os.getenv("BITGET_DEMO_API_KEY")) if is_demo else quote_plus(os.getenv("BITGET_API_KEY"))
api_secret_key = quote_plus(os.getenv("BITGET_DEMO_SECRET_KEY"))  if is_demo else quote_plus(os.getenv("BITGET_SECRET_KEY"))
passphrase = quote_plus(os.getenv("BITGET_PASSPHRASE"))



marketApi =MarketApi(api_key, api_secret_key, passphrase, is_demo=is_demo)
orderApi =OrderApi(api_key, api_secret_key, passphrase, is_demo=is_demo)
accountApi =AccountApi(api_key, api_secret_key, passphrase, is_demo=is_demo)
bitgetApi =BitgetApi(api_key, api_secret_key, passphrase, is_demo=is_demo)



def handel_error(message):
    print("handle_error:" + message)


def get_ws_client():
    return BitgetWsClient(c.CONTRACT_DEMO_WS_URL if is_demo else c.CONTRACT_WS_URL, need_login=False) \
            .api_key(api_key) \
            .api_secret_key(api_secret_key) \
            .passphrase(passphrase) \
            .error_listener(handel_error) \
            .build()
