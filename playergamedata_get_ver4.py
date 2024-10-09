from mwrogue.esports_client import EsportsClient
from bs4 import BeautifulSoup
import json
import os, shutil

site = EsportsClient("lol")
start_date = "2023-01-01"
end_date = "2024-01-01"

def gameid_get(player_id):
    result = []

    overview_page = site.cargo_client.query(
        tables="PlayerRedirects=PR",
        fields="PR.OverviewPage",
        where=f"PR.ID='{player_id}'"
    )

    player_name = list(overview_page[0].items())[0][1]

    response = site.cargo_client.query(
        tables="ScoreboardGames=SG, ScoreboardPlayers=SP, PlayerRedirects=PR",
        fields="SG.RiotPlatformGameId, SG.GameId, PR.ID",
        where=f"PR.OverviewPage='{player_name}' AND SP.GameId=SG.GameId AND SP.DateTime_UTC>='{start_date} 00:00:00' AND SP.DateTime_UTC<'{end_date} 00:00:00'",
        join_on="SP.Link=PR.AllName, SP.GameId=SG.GameId",
        order_by="SP.DateTime_UTC"
    )

    for x in range(len(response)):
        if list(response[x].items())[0][1] is not None:
            result.append(list(response[x].items()))
        else:
            continue
    return result

def gamedata_get(gameid_name):
    try:
        data, timeline = site.get_data_and_timeline(f"{gameid_name}", version=5)
    except KeyError:
        data, timeline = site.get_data_and_timeline(f"{gameid_name}", version=4)
    return data, timeline

if __name__ == "__main__":
    player_id = "Faker"
    gameid = gameid_get(player_id)
    
    for i in range(len(gameid)):
        gameid_name = gameid[i][0][1]
        gamedata, gametimeline = gamedata_get(gameid_name)

        file_name = f"playergamedata_ver4_test_{gameid_name}.json"
        with open(file_name, "w+") as jsonFile:
            jsonFile.write(json.dumps(gamedata, indent = 4))
        
        file_name = f"playergametimeline_ver4_test_{gameid_name}.json"
        with open(file_name, "w+") as jsonFile:
            jsonFile.write(json.dumps(gametimeline, indent = 4))

        print(f"{i+1} / {len(gameid)}")
    
    print("END")