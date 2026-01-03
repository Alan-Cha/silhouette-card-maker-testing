from plugins.star_wars_unlimited.swudb import fetch_name_and_title, request_swudb, SWUDB_CARD_NUMBER_URL_TEMPLATE

def test_tyrannus_typo():
  # SWUDB incorrectly returns subtitle Darth Tyrannus for Count Dooku card
  # The correct subtitle is Darth Tyranus
  json = request_swudb(SWUDB_CARD_NUMBER_URL_TEMPLATE.format(set_id="SOR", set_number="304")).json()
  raw_name = json.get('Name')
  raw_title = json.get('Subtitle') or '' if json.get('Type') != 'Base' else ''
  assert raw_name == "Count Dooku"
  assert raw_title == "Darth Tyrannus"

  name, title = fetch_name_and_title("SOR_304")
  assert name == "Count Dooku"
  assert title == "Darth Tyranus"