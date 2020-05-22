import requests
from bs4 import BeautifulSoup

uswnt_URL = 'https://www.ussoccer.com/players'
players_page = requests.get(uswnt_URL)

soup = BeautifulSoup(players_page.content, 'html.parser')

results = soup.find(id='uswnt')

players = results.find_all('div', class_='PlayerThumbnail-module__playerName--2bbtZ')

for player in players:
    player_info = (player.text).split()
    player_num = player_info[0]
    player_fname = (player_info[1]).replace("'", "")
    player_lname = (player_info[2]).replace("'", "")


    player_stats_URL = uswnt_URL + "/" + player_lname[0].lower() + "/" + player_fname.lower() + "-" + player_lname.lower()
    player_stats_page = requests.get(player_stats_URL)
    stat_soup = BeautifulSoup(player_stats_page.content, 'html.parser')
    stat_results = stat_soup.find(id='player-overview')
    stats = stat_results.find('div', class_='P1Player-module__textColumn--24s4m')
    lis = stats.find_all('li')
    is_goal_keeper = False
    print(player_fname, player_lname)
    for li in lis:
        print(li.text)
        if(li.text == "Position Goalkeeper"):
            is_goal_keeper = True

    more_stats = (stat_results.find_all('div', class_='HighlightStats-module__value--6exAY'))
    temp = []
    for s in more_stats:
        temp.append(s.text)

    print("Appearances", temp[0])
    print("Goals", temp[1])
    if(not is_goal_keeper):
        print("Assists", temp[2])
    print()

