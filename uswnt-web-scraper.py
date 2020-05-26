# Import libraries
import requests
from bs4 import BeautifulSoup

# Site we want to scrape
uswnt_URL = 'https://www.ussoccer.com/players'
players_page = requests.get(uswnt_URL)
soup = BeautifulSoup(players_page.content, 'html.parser')
results = soup.find(id='uswnt')

# Get all the players div
players = results.find_all('div', class_='PlayerThumbnail-module__playerName--2bbtZ')

# Print out each player's info and stats
for player in players:
    player_info = (player.text).split()
    player_num = player_info[0]
    player_fname = (player_info[1]).replace("'", "")
    player_lname = (player_info[2]).replace("'", "")

    # Player URL
    players_URL = uswnt_URL + "/" + player_lname[0].lower() + "/" + player_fname.lower() + "-" + player_lname.lower()
    players_page = requests.get(players_URL)
    players_info_soup = BeautifulSoup(players_page.content, 'html.parser')
    players_info_results = players_info_soup.find(id='player-overview')

    # Get player's information
    players_info = players_info_results.find('div', class_='P1Player-module__textColumn--24s4m')
    player_background = players_info.find_all('li')

    # Goalkeeper's have different stats
    is_goal_keeper = False

    # Print player's full name
    print(player_fname, player_lname)

    # Print player's background information
    for player in player_background:
        print(player.text)
        if(player.text == "Position Goalkeeper"):
            is_goal_keeper = True

    # Stats for each player
    player_stats = (players_info_results.find_all('div', class_='HighlightStats-module__value--6exAY'))
    temp = []
    for stat in player_stats:
        temp.append(stat.text)

    # Number of world cups won
    num_wc = 0
    wc = players_info.find('div', class_='HighlightStats-module__starContainer--3J-I7')
    if(wc is not None):
        wc_stars = wc.findChildren("svg" , recursive=False)
        num_wc = len(wc_stars)

    # Print the stats
    print("Appearances", temp[0])
    if(not is_goal_keeper):
        print("Goals", temp[1])
        print("Assists", temp[2])
    else:
        print("Clean Sheets", temp[1])
    print("World Cups", num_wc)
    print()

