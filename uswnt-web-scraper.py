# Import libraries
import sys
import requests
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient

# Initalize and declare variables
uswnt_URL, db, collection = 'https://www.ussoccer.com/players', None, None

# Get the div of all players
def get_players_div():
    players_page = requests.get(uswnt_URL)
    soup = BeautifulSoup(players_page.content, 'html.parser')
    results = soup.find(id='uswnt')

    # Get all the players div
    return results.find_all('div', class_='PlayerThumbnail-module__playerName--2bbtZ')

# Get player URL
def get_player_url(lname, fname):
    # Player URL
    players_URL = uswnt_URL + "/" + lname[0].lower() + "/" + fname.lower() + "-" + lname.lower()
    players_page = requests.get(players_URL)
    players_info_soup = BeautifulSoup(players_page.content, 'html.parser')
    return players_info_soup.find(id='player-overview')

# Update database with data
def update_db(position, number, fname, lname, dob, hometown, height, club, appearances, goals, assists, clean_sheets, world_cups):
        doc = None
        if(position != "Goalkeeper"):
            doc = {"_id": number, "backround":{"fname": fname, "lname": lname, "position": position, "number": number, "dob": dob, "hometown": hometown, "height": height, "club": club}, "stats": {"appearances": appearances, "goals": goals, "assists": assists, "world_cups": world_cups} }
        else:
            doc = {"_id": number, "backround":{"fname": fname, "lname": lname, "position": position, "number": number, "dob": dob, "hometown": hometown, "height": height, "club": club}, "stats": {"appearances": appearances, "clean_sheets": clean_sheets, "world_cups": world_cups} }

        collection.update_one({"_id": number},{"$set" :doc}, upsert=True)

# Get number of world cups played by player
def get_num_wc(players_info):
    # Number of world cups won
    num_wc = 0
    wc = players_info.find('div', class_='HighlightStats-module__starContainer--3J-I7')
    if(wc is not None):
        wc_stars = wc.findChildren("svg" , recursive=False)
        num_wc = len(wc_stars)
    return num_wc

# Get player's info
def get_player_info(players):
    for player in players:
        player_info = (player.text).split()
        player_num = player_info[0]
        fname = (player_info[1]).replace("'", "")
        lname = (player_info[2]).replace("'", "")

        # Player URL
        players_info_results = get_player_url(lname, fname)

        # Get player's information
        players_info = players_info_results.find('div', class_='P1Player-module__textColumn--24s4m')
        player_background = players_info.find_all('li')

        position, number, dob, hometown, height, club = None, None, None, None, None, None

        # Set player's background information
        for info in player_background:
            if("Position" in info):
                position = (info.text).replace("Position ", "")
            if("Number" in info):
                number = (info.text).replace("Number ", "")
            if("Date of Birth" in info):
                dob = (info.text).replace("Date of Birth ", "")
            if("Hometown" in info):
                hometown = (info.text).replace("Hometown ", "")
            if("Height" in info):
                height = (info.text).replace("Height ", "")
            if("Club" in info):
                club = (info.text).replace("Club ", "")

        # Stats for each player
        player_stats = (players_info_results.find_all('div', class_='HighlightStats-module__value--6exAY'))
        temp = []

        for stat in player_stats:
            temp.append(stat.text)

        # Number of world cups won
        num_wc = get_num_wc(players_info)

        appearances, goals, assists, clean_sheets = temp[0], None, None, None

        if(position != "Goalkeeper"):
            goals, assists = temp[1], temp[2]
        else:
            clean_sheets = temp[1]
        world_cups = num_wc

        update_db(position, number, fname, lname, dob, hometown, height, club, appearances, goals, assists, clean_sheets, world_cups)


if __name__ == "__main__":
    username = input("Enter username: ")
    password = input("Enter password: ")

    cluster = MongoClient(f"mongodb+srv://{username}:{password}@cluster0.dz1fr.mongodb.net/uswnt?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority")

    db = cluster["uswnt"]
    collection = db["players"]

    print()
    print("Updating database...")

    players = get_players_div()
    get_player_info(players)

    print()
    print("Finished updating database")
