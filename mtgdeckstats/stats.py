import re
import hashlib
from io import StringIO
from mtgtools.MtgDB import MtgDB, PCardList
from .mtgdb import get_mtgdb

COST_MATRIX = {"5C": [7,9,10],
"4C": [8,9,11],
"3C": [9,10,12],
"2C": [10,12,13],
"5CC": [10,12,15],
"1C": [11,13,14],
"4CC": [11,13,16],
"C": [12,14,15],
"3CC": [12,15,17],
"4CCC": [12,16,19],
"2CC": [13,16,19] ,
"3CCC": [14,17,20],
"1CC": [15,18,21],
"2CCC": [15,19,22],
"CC": [18,21,23],
"1CCC": [17,21,24],
"1CCCC": [18,22,26],
"CCC": [19,23,27],
"CCCC": [20,24,29]}

def convert_deck(deck_raw:str):
  deck_str = StringIO()
  sideboard = False
  for line in deck_raw.split("\n"):
    
    if line.startswith("Sideboard"):
      sideboard = True
    if line != "" and line[0].isdigit():
      m = re.match(r"(\d+) (.*) \((.*)\)", line)
      g = m.groups()
      if sideboard:
        deck_str.write("SB: ")
      deck_str.write(f"{g[0]} {g[1]} [{g[2].lower()}]\n")
  return deck_str.getvalue()

def convert_multicolored(mana_cost, color):
  cleaned = mana_cost.replace("}","") \
    .replace("{","")
  final = ""
  count = 0
  for p in cleaned:
    if p.isdigit():
      count = int(p)
    elif p == color:
      final += "C"
    else:
      count += 1
  
  return f"{count}{final}" if count > 0 else final

def search_cached(deck_str):
  mtg_db:MtgDB = get_mtgdb()
  cards:PCardList = mtg_db.root.scryfall_cards
  deck_hash = hashlib.md5(deck_str.encode()).hexdigest()
  try:
    deck = getattr(mtg_db.root, deck_hash)
  except AttributeError:
    deck = cards.from_str(deck_str)
    setattr(mtg_db.root, deck_hash, deck)
    mtg_db.commit()
  return deck
    
def get_stats(deck_str):
  deck = search_cached(deck_str)
  # mtg_db:MtgDB = get_mtgdb()
  # cards:PCardList = mtg_db.root.scryfall_cards
  # deck = cards.from_str(deck_str)
  no_land_deck = [card for card in deck if card.cmc > 0]
  lands = [card for card in deck if card.cmc == 0]
  
  heading = ["", "-"]
  colors = set()
  card_count = len(no_land_deck)
  all_costs = 0
  costs = set()
  colors_count = {}
  colorless_count = 0
  pure_colors_count = {}
  multicolor_count = 0
  mana_sources = {}
  for land in lands:
    for c in land.color_identity:      
      if mana_sources.get(c) is None:
        mana_sources[c] = 0
      mana_sources[c] += 1
  for entry in no_land_deck: 
    
    
    # analyze colors
    if entry.mana_cost is None:
      card_mana_cost = entry.card_faces[0]['mana_cost']
      card_colors = entry.card_faces[0]['colors']
    else:
      card_mana_cost = entry.mana_cost
      card_colors = entry.colors
    all_costs += entry.cmc
    print(entry.name, card_mana_cost, card_colors)
    if card_colors is not None and card_colors != []:
      for color in card_colors:
        colors.add(color)
        if colors_count.get(color) is None:
          colors_count[color] = 0
        colors_count[color] += 1
        mana_cost = convert_multicolored(card_mana_cost, color)
        sources = COST_MATRIX[mana_cost][1]
        t = (mana_cost, color, sources)
        costs.add(t)
      if len(card_colors) > 1:
        multicolor_count += 1
      else:
        if pure_colors_count.get(card_colors[0]) is None:
          pure_colors_count[card_colors[0]] = 0
        pure_colors_count[card_colors[0]] += 1
    else:
      colorless_count += 1
      
    
  
  needs = {}
  for (_, color, sources) in costs:
    if not needs.get(color) or sources > needs[color]:
      needs[color] = sources
  colors = list(colors)
  heading += colors
  rows = []
  
  rows.append(["lands", len(lands)] + ["-"] * len(colors))    
  rows.append(["non lands", card_count] + ["-"] * len(colors))    
  rows.append(["avg mana cost", "%.2f" % (all_costs/card_count)] + ["-"] * len(colors))    
  rows.append(["multicolor", multicolor_count] + ["-"] * len(colors))
  rows.append(["colorless", colorless_count] + ["-"] * len(colors))    
  rows.append(["colored", ""] + [pure_colors_count[c] for c in colors])    
  rows.append(["color identity", ""] + [colors_count[c] for c in colors])    
  rows.append(["colors %", ""] + ["%.2f%%" % (colors_count[c]/card_count*100) for c in colors])    
  rows.append(["color sources", ""] + [mana_sources[c] for c in colors])
  rows.append(["needed lands", len(lands)] + ["-"] * len(colors))    
  rows.append(["needed sources", ""] + [needs[c] for c in colors])    
  return {
    "heading": heading,
    "rows": rows,
  }