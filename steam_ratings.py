#!/usr/bin/env python

STEAM_WEB_API_KEY = ''
STEAM_ID = ''


import os
import requests
import bs4
import json

steam_ratings_folder = "Steam Ratings"
if not os.path.exists(steam_ratings_folder):
	os.makedirs(steam_ratings_folder)

steam_overwhelmingly_positive_file = open(os.path.join(steam_ratings_folder, "overwhelmingly_positive_steam_games.txt"), "w")
steam_very_positive_file = open(os.path.join(steam_ratings_folder, "very_positive_steam_games.txt"), "w")

steam_mostly_positive_file = open(os.path.join(steam_ratings_folder, "positive_steam_games.txt"), "w")
steam_mixed_file = open(os.path.join(steam_ratings_folder, "mixed_reviews_steam_games.txt"), "w")

steam_negative_file = open(os.path.join(steam_ratings_folder, "negative_reviews_steam_games.txt"), "w")

steam_positive_file = open(os.path.join(steam_ratings_folder, "positive_steam_games.txt"), "w")
steam_non_parsed_games_file = open(os.path.join(steam_ratings_folder, "non_parsed_games.txt"), "w")

owned_games_url = 'http://api.steampowered.com/IPlayerService/'\
				  + 'GetOwnedGames/v0001/?'\
				  + 'key=' + STEAM_WEB_API_KEY\
				  + '&steamid=' + STEAM_ID\
				  + '&format=json'
owned_games_json = requests.get(owned_games_url).text
owned_games = json.loads(owned_games_json)['response']['games']

print str(len(owned_games)) + " game pages to parse...\n"
print ""

total_reviews_found, non_parsed_games, no_store_page_games = 0, 0, 0
non_parsed_games_info = "LIST OF NON-PARSED GAME PAGES\n"
no_store_page_games_info = "LIST OF GAME PAGES WITH NO STORE PAGES\n"
for idx, game in enumerate(owned_games):
	game_appid = str(game[u'appid'])
	game_page_url = 'http://store.steampowered.com/app/' + game_appid
	game_page = requests.get(game_page_url).text.encode('utf-8')
	soup = bs4.BeautifulSoup(game_page, "html.parser")
	game_name = soup.find('div', 'apphub_AppName')
	game_review_tag = soup.find('span', 'game_review_summary')
	game_name_text = game_name.text.encode('utf-8') if game_review_tag\
					 else None
	if game_review_tag:
		print str(idx+1) + ". " + game_name_text + "\t --- \t" + game_review_tag.text.encode('utf-8')
		if game_review_tag.text == "Overwhelmingly Positive": 
			steam_overwhelmingly_positive_file.write(game_name_text+"\n")
		if game_review_tag.text == "Very Positive": 
			steam_very_positive_file.write(game_name_text+"\n")
		if game_review_tag.text == "Mostly Positive": 
			steam_mostly_positive_file.write(game_name_text+"\n")
		if game_review_tag.text == "Positive": 
			steam_positive_file.write(game_name_text+"\n")
		if game_review_tag.text == "Mixed": 
			steam_mixed_file.write(game_name_text+"\n")
		if game_review_tag.text == "Negative" or\
		   game_review_tag.text == "Mostly Negative" or\
		   game_review_tag.text == "Very Negative" or\
		   game_review_tag.text == "Overwhelmingly Negative": steam_negative_file.write(game_name_text+"\n")
		total_reviews_found += 1
	else:
		game_name_text = soup.find('title').text.encode('utf-8')
		if game_name_text == "Welcome to Steam":
			no_store_page_games_info += str(idx+1) + ". " + "NO STORE PAGE" + "\t---\t" + "Game APP ID: " + game_appid + "\n"
			no_store_page_games += 1
		else:
			game_name_text = game_name_text[:game_name_text.find("on Steam")]
			non_parsed_games_info += str(idx+1) + ". " + game_name_text + "\t---\t" + "Game Store Page: "  + game_page_url + "\n"
			non_parsed_games += 1

print ""
print non_parsed_games_info + "\n" + no_store_page_games_info
steam_non_parsed_games_file.write(non_parsed_games_info + "\n" + no_store_page_games_info)

steam_overwhelmingly_positive_file.close()
steam_very_positive_file.close()
steam_mostly_positive_file.close()
steam_positive_file.close()
steam_mixed_file.close()
steam_negative_file.close()
steam_non_parsed_games_file.close()

print ""
print "Done! " +\
	  str(total_reviews_found) + " of " + str(len(owned_games)) + " games' reviews info. parsed, " +\
	  str(non_parsed_games) + " games were unable to be parsed (probable reason: age gate), and " +\
	  str(no_store_page_games) + " games had no store pages."
print ""