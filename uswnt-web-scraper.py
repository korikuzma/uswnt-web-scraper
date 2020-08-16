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
            doc = {"_id": number, "fname": fname, "lname": lname, "position": position, "number": int(number), "dob": dob, "hometown": hometown, "height": height, "club": club, "appearances": int(appearances), "goals": int(goals), "assists": int(assists), "world_cups": int(world_cups)}
        else:
            doc = {"_id": number, "fname": fname, "lname": lname, "position": position, "number": int(number), "dob": dob, "hometown": hometown, "height": height, "club": club, "appearances": int(appearances), "clean_sheets": int(clean_sheets), "world_cups": int(world_cups)}

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

# Retreive the max key from the database
def max_arg(key):
    max_key = collection.find_one(sort=[(key, -1)])
    print(max_key["fname"], max_key["lname"], ":" ,max_key[key], key)

# Ask user if they would like to view stats
def find_max():
    max_input = input("Would you like to know the player with the highest stats in a category? y/n ")
    while(max_input.lower().strip() == 'y'):
        while True:
            find_max = input("Enter goals, appearances, assists, or clean_sheets to find the player with the max. : ")
            find_max = find_max.lower().strip()
            if((find_max == "goals") | (find_max == "appearances") | (find_max == "assists") | (find_max == "clean_sheets")):
                max_arg(find_max.lower())
                max_input = input("Do you want to know another? y/n ")
                break
            else:
                print("Error: Invalid input. Try again.")

# Print all players with  info sorted by number
def display_all_players():
    display_input = input("Would you like to display all the players information? y/n ")
    if(display_input.lower().strip() == 'y'):
        for doc in collection.find().sort("number"):
            print (doc["fname"], doc["lname"])
            print("Number:", doc["number"])
            print("Position:", doc["position"])
            print("Hometown:", doc["hometown"])
            print("Birthday:", doc["dob"])
            print("Height:", doc["height"])
            print("Club:", doc["club"])
            print()

# Display individual player's stats and background info
def display_player():
    player_input = input("Would you like to know the player with the highest stats in a category? y/n ")
    while(player_input.lower().strip() == 'y'):
        while True:
            try:
                lname_input = input("Enter the last name of the player you'd like to see: ")
                query = {"lname": lname_input.title().strip()}
                doc = collection.find_one(query)
                print (doc["fname"], doc["lname"])
                print("Number:", doc["number"])
                print("Position:", doc["position"])
                print("Appearances:", doc["appearances"])

                # Goalies have different fields
                if(doc["position"] != "Goalkeeper"):
                    print("Goals:", doc["goals"])
                    print("Assists:", doc["assists"])
                else:
                    print("Clean Sheets:", doc["clean_sheets"])

                print("Club:", doc["club"])
                print("Hometown:", doc["hometown"])
                print("Birthday:", doc["dob"])
                print("Height:", doc["height"])
                print()
                player_input = input("Would you like to know another the player with the highest stats in a category? y/n ")
                break
            except:
                print("Invalid last name of player")

if __name__ == "__main__":

    while True:
        try:
            username = input("Enter username: ")
            password = input("Enter password: ")

            cluster = MongoClient(f"mongodb+srv://{username.strip()}:{password.strip()}@cluster0.dz1fr.mongodb.net/uswnt?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority")

            db = cluster["uswnt"]
            collection = db["players"]

            players = get_players_div()
            get_player_info(players)

            break
        except (pymongo.errors.OperationFailure, pymongo.errors.ConfigurationError):
            print("Wrong username and/or password.")

    print("Finished updating database")
    print()

    display_all_players()
    find_max()
    display_player()

    print("Goodbye!")