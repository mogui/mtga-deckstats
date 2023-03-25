from flask import current_app, g
import requests
from loguru import logger
import time

BASE_URL="https://api.scryfall.com"

class MtgRepo():
    def __init__(self) -> None:
       self.base = BASE_URL
   
    def get_card(self, set, cn):
      """Get a card from scryfall"""
      time.sleep(70/1000)
      ret = requests.get(f"{self.base}/cards/{set.lower()}/{cn}")
      logger.debug(" ".join([set, cn, str(ret.status_code)]))
      if ret.status_code == 200:
        return ret.json()
      else:
        return None
      

def get_repo():
    if 'mtgrepo' not in g:
        g.mtgrepo = MtgRepo()
    return g.mtgrepo

# def init_app(app):
#     app.teardown_appcontext(close_db)
    