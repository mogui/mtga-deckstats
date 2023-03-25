import re
import json
import click
from munch import DefaultMunch
from .mtgrepo import get_repo
from loguru import logger

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

def init_app(app):
    app.cli.add_command(convert_file)
    
@click.command('convert')
@click.argument('input', type=click.File('r'))
def convert_file(input):
  """Converts given text file in arena format"""
  click.echo('Converting.')
  deck_str = input.read()
  c = convert_deck(deck_str)
  print(json.dumps(c, indent=2))
  
    

def convert_deck(deck_raw:str):
  sideboard = False
  deck = []
  repo = get_repo()
  mapped_keys = [
    'mana_cost', 
    'cmc', 
    'type_line', 
    'color_identity', 
    'colors',
    'set_name', 
    'name',
    'card_faces'
  ]
  for line in deck_raw.split("\n"):
    if line.startswith("Sideboard"):
      sideboard = True
    if line != "" and line[0].isdigit():
      # 4 Fable of the Mirror-Breaker (NEO) 141
      # ?P<name>
      logger.debug(line)
      m = re.match(r"(?P<qt>\d+) (?P<name>.*) \((?P<set>[a-zA-Z0-9]{3})\) (?P<cn>\d+)", line) 
      logger.debug(line)
      
      # resolve card
      scry_card = repo.get_card(m.group("set"), m.group("cn"))
      if scry_card is None:
        continue
      card = {k: v for k,v in scry_card.items() if k in mapped_keys}
      card['sideboard'] = sideboard
      for _ in range(0, int(m.group("qt"))):
        deck.append(DefaultMunch.fromDict(card, None))
      
  return deck

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

    
def get_stats(deck_str):
  deck = convert_deck(deck_str)
  
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
      card_mana_cost = entry.card_faces[0].mana_cost
      card_colors = entry.card_faces[0].colors
    else:
      card_mana_cost = entry.mana_cost
      card_colors = entry.colors
    all_costs += entry.cmc
    logger.debug(entry.name, card_mana_cost, card_colors)
    if card_colors is not None and card_colors != []:
      for color in card_colors:
        colors.add(color)
        if colors_count.get(color) is None:
          colors_count[color] = 0
        colors_count[color] += 1
        mana_cost = convert_multicolored(card_mana_cost, color)
        logger.debug(mana_cost)
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
  # rows.append(["needed lands", len(lands)] + ["-"] * len(colors))    
  rows.append(["needed sources", ""] + [needs[c] for c in colors])    
  rows.append(["color sources", ""] + [mana_sources[c] for c in colors if mana_sources.get(c)])
  return {
    "heading": heading,
    "rows": rows,
  }