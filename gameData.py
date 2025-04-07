from mwrogue.esports_client import EsportsClient
import requests
import json
import pandas as pd
import os
import datetime

site = EsportsClient("lol")
start_date = "2024-01-01"
end_date = "2024-12-31"

def gameidGet(tournament):
    result = []
    response = site.cargo_client.query(
        tables="ScoreboardGames=SG",
        fields="SG.RiotPlatformGameId",
        where=f"SG.Tournament='{tournament}' AND SG.DateTime_UTC>='{start_date} 00:00:00' AND SG.DateTime_UTC<='{end_date} 23:59:59'",
        order_by="SG.DateTime_UTC"
    )
    for i in range(len(response)):
        if list(response[i].items())[0][1] is not None:
            result.append(list(response[i].items())[0][1])
        else:
            continue
    return result

def oraclesDataGet(orc_csv, gameId):
    datalist = []
    filtered_csv = orc_csv[orc_csv["gameid"] == gameId]
    filtered_csv = filtered_csv.reset_index(drop=True)

    for i in range(10):
        newdata = []
        newdata.append(filtered_csv.iloc[i, 0])
        for j in range(3, 14):
            newdata.append(filtered_csv.iloc[i, j])
        newdata.append(filtered_csv.iloc[i, 15])
        newdata.append(filtered_csv.iloc[i, 17])
        for j in range(18, 23):
            newdata.append(filtered_csv.iloc[i, j])
        for j in range(18, 23):
            if i < 5:
                newdata.append(filtered_csv.iloc[11, j])
            else:
                newdata.append(filtered_csv.iloc[10, j])
        for j in range(23, 28):
            if i < 5:
                newdata.append(filtered_csv.iloc[10, j])
            else:
                newdata.append(filtered_csv.iloc[11, j])
        for j in range(23, 28):
            if i < 5:
                newdata.append(filtered_csv.iloc[11, j])
            else:
                newdata.append(filtered_csv.iloc[10, j])
        for j in range(28, 45):
            newdata.append(filtered_csv.iloc[i, j])
        for j in range(45, 56):
            if i < 5:
                newdata.append(filtered_csv.iloc[10, j])
            else:
                newdata.append(filtered_csv.iloc[11, j])
        for j in range(57, 76):
            if i < 5:
                newdata.append(filtered_csv.iloc[10, j])
            else:
                newdata.append(filtered_csv.iloc[11, j])
        for j in range(76, 93):
            newdata.append(filtered_csv.iloc[i, j])
        for j in range(95, 98):
            newdata.append(filtered_csv.iloc[i, j])
        for j in range(100, 161):
            newdata.append(filtered_csv.iloc[i, j])
        datalist.append(newdata)
    return datalist

def idNameGet(gameVer, itemId=None, styleId=None, runeId=None):
    def getItemName(id):
        url = f"https://ddragon.leagueoflegends.com/cdn/{gameVer}/data/en_US/item.json"
        response = requests.get(url)
        response.raise_for_status()
        itemData = response.json()
        itemList = itemData["data"]
        for key, value in itemList.items():
            if key == str(id):
                return itemList[key]["name"]
        return False
    
    def getRuneName(styleId, runeId):
        url = f"https://ddragon.leagueoflegends.com/cdn/{gameVer}/data/en_US/runesReforged.json"
        response = requests.get(url)
        response.raise_for_status()
        runeData = response.json()
        for i in range(len(runeData)):
            if runeData[i]["id"] == styleId:
                for j in range(len(runeData[i]["slots"])):
                    for k in range(len(runeData[i]["slots"][j]["runes"])):
                        if runeData[i]["slots"][j]["runes"][k]["id"] == runeId:
                            return runeData[i]["slots"][j]["runes"][k]["key"]
        return False

    '''
    def getChampionName(id):
        url = f"https://ddragon.leagueoflegends.com/cdn/{gameVer}/data/en_US/champion.json"
        response = requests.get(url)
        response.raise_for_status()
        championData = response.json()
        championList = championData["data"]
        for key, value in championList.items():
            if championList[key]["key"] == str(id):
                return championList[key]["id"]
        return False
    '''

    try:
        if itemId != None:
            nameExist = getItemName(itemId)
        elif runeId != None:
            nameExist = getRuneName(styleId, runeId)
        # elif championId != None:
            # nameExist = getChampionName(championId)
        if nameExist:
            return nameExist
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except IndexError:
        print("Error: No versions found in the API response.")

def mwrogueDataGet(gameId):
    gameData, gameTimeline = site.get_data_and_timeline(f"{gameId}", version=5)
    mw_json = gameData

    datalist = []
    for i in range(10):
        newdata = []
        newdata.append(mw_json["participants"][i].get("champLevel"))
        if i < 5:
            opp_id = i + 5
        else:
            opp_id = i - 5
        newdata.append(mw_json["participants"][opp_id].get("riotIdGameName").split(" ")[1])
        newdata.append(mw_json["participants"][opp_id].get("championName"))
        newdata.append(mw_json["participants"][i]["challenges"].get("maxCsAdvantageOnLaneOpponent"))
        newdata.append(mw_json["participants"][i]["challenges"].get("maxLevelLeadLaneOpponent"))
        newdata.append(mw_json["participants"][i]["challenges"].get("killsNearEnemyTurret"))
        newdata.append(mw_json["participants"][i]["challenges"].get("killsUnderOwnTurret"))
        newdata.append(mw_json["participants"][i]["challenges"].get("soloKills"))
        newdata.append(mw_json["participants"][i].get("damageDealtToTurrets"))
        newdata.append(mw_json["participants"][i]["challenges"].get("firstTurretKilledTime"))
        newdata.append(mw_json["participants"][i]["challenges"].get("stealthWardsPlaced"))
        newdata.append(mw_json["participants"][i]["challenges"].get("controlWardsPlaced"))
        newdata.append(mw_json["participants"][i].get("detectorWardsPlaced"))
        newdata.append(mw_json["participants"][i]["challenges"].get("wardTakedownsBefore20M"))
        newdata.append(mw_json["participants"][i]["challenges"].get("controlWardTimeCoverageInRiverOrEnemyHalf"))
        newdata.append(mw_json["participants"][i]["challenges"].get("wardsGuarded"))
        newdata.append(mw_json["participants"][i]["challenges"].get("epicMonsterSteals") + mw_json["participants"][i]["challenges"].get("epicMonsterStolenWithoutSmite"))
        newdata.append(mw_json["participants"][i]["challenges"].get("jungleCsBefore10Minutes"))
        newdata.append(mw_json["participants"][i]["challenges"].get("initialCrabCount"))
        newdata.append(mw_json["participants"][i]["challenges"].get("scuttleCrabKills"))
        newdata.append(mw_json["participants"][i]["totalAllyJungleMinionsKilled"])
        newdata.append(mw_json["participants"][i]["totalEnemyJungleMinionsKilled"])
        newdata.append(mw_json["participants"][i]["challenges"].get("earliestBaron"))
        newdata.append(mw_json["participants"][i]["challenges"].get("completeSupportQuestInTime"))
        newdata.append(mw_json["participants"][i]["challenges"].get("saveAllyFromDeath"))
        newdata.append(mw_json["participants"][i].get("totalDamageShieldedOnTeammates"))
        newdata.append(mw_json["participants"][i].get("totalHealsOnTeammates"))
        newdata.append(mw_json["participants"][i].get("totalTimeCCDealt"))
        newdata.append(mw_json["participants"][i]["challenges"].get("effectiveHealAndShielding"))
        newdata.append(mw_json["participants"][i]["challenges"].get("enemyChampionImmobilizations"))
        newdata.append(mw_json["participants"][i]["challenges"].get("skillshotsHit"))
        newdata.append(mw_json["participants"][i]["challenges"].get("skillshotsDodged"))
        gameVer = str(".".join(mw_json.get("gameVersion").split(".")[:2])) + ".1"
        newdata.append(idNameGet(gameVer, itemId=mw_json["participants"][i].get("item0")))
        newdata.append(idNameGet(gameVer, itemId=mw_json["participants"][i].get("item1")))
        newdata.append(idNameGet(gameVer, itemId=mw_json["participants"][i].get("item2")))
        newdata.append(idNameGet(gameVer, itemId=mw_json["participants"][i].get("item3")))
        newdata.append(idNameGet(gameVer, itemId=mw_json["participants"][i].get("item4")))
        newdata.append(idNameGet(gameVer, itemId=mw_json["participants"][i].get("item5")))
        newdata.append(idNameGet(gameVer, 
                                styleId=mw_json["participants"][i]["perks"]["styles"][0].get("style"),
                                runeId=mw_json["participants"][i]["perks"]["styles"][0]["selections"][0].get("perk")))
        newdata.append(idNameGet(gameVer, 
                                styleId=mw_json["participants"][i]["perks"]["styles"][0].get("style"),
                                runeId=mw_json["participants"][i]["perks"]["styles"][0]["selections"][1].get("perk")))
        newdata.append(idNameGet(gameVer, 
                                styleId=mw_json["participants"][i]["perks"]["styles"][0].get("style"),
                                runeId=mw_json["participants"][i]["perks"]["styles"][0]["selections"][2].get("perk")))
        newdata.append(idNameGet(gameVer, 
                                styleId=mw_json["participants"][i]["perks"]["styles"][0].get("style"),
                                runeId=mw_json["participants"][i]["perks"]["styles"][0]["selections"][3].get("perk")))
        newdata.append(idNameGet(gameVer, 
                                styleId=mw_json["participants"][i]["perks"]["styles"][1].get("style"),
                                runeId=mw_json["participants"][i]["perks"]["styles"][1]["selections"][0].get("perk")))
        newdata.append(idNameGet(gameVer, 
                                styleId=mw_json["participants"][i]["perks"]["styles"][1].get("style"),
                                runeId=mw_json["participants"][i]["perks"]["styles"][1]["selections"][1].get("perk")))
        if mw_json["participants"][i]["missions"].get("ActMission_S1_A2_FeatsOfStrength") != None:
            if mw_json["participants"][i]["missions"].get("ActMission_S1_A2_FeatsOfStrength") >= 2:
                featsOfStrength = True
            else:
                featsOfStrength = False
            newdata.append(featsOfStrength)
        else:
            newdata.append(None)
        newdata.append(mw_json["participants"][i]["missions"].get("SeasonalMissions_TakedownAtakhan"))
        datalist.append(newdata)
    return datalist

def datasetHeader():
    header = [
        # Data from Orcales
        "gameId",
        "league",
        "year",
        "split", 
        "playoffs", 
        "date", 
        "game", 
        "patch", 
        "participantId", 
        "side",
        "position", 
        "playerName",
        "teamName",
        "champion", 
        "ban1", 
        "ban2", 
        "ban3", 
        "ban4", 
        "ban5",
        "opp_ban1", 
        "opp_ban2", 
        "opp_ban3", 
        "opp_ban4", 
        "opp_ban5", 
        "pick1", 
        "pick2",
        "pick3", 
        "pick4", 
        "pick5", 
        "opp_pick1", 
        "opp_pick2",
        "opp_pick3", 
        "opp_pick4", 
        "opp_pick5", 
        "gamelength", 
        "win", 
        "kills", 
        "deaths", 
        "assists", 
        "teamKills", 
        "teamDeaths", 
        "doublekills", 
        "triplekills", 
        "quadrakills", 
        "pentakills", 
        "firstblood", 
        "firstbloodKill", 
        "firstbloodAssist", 
        "firstbloodVictim",
        "teamKpm",
        "ckpm",
        "firstdragon",
        "dragons",
        "opp_dragons",
        "elementalDrakes",
        "opp_elementalDrakes",
        "infernals",
        "mountains",
        "clouds",
        "oceans",
        "chemtechs",
        "hextechs",
        "elders",
        "opp_elders",
        "firstherald", 
        "heralds",
        "opp_heralds",
        "voidgrubs",
        "opp_voidgrubs",
        "firstBaron", 
        "barons",
        "opp_barons",
        "firsttower", 
        "towers", 
        "opp_towers",
        "firstMidTower",
        "firstToThreeTowers",
        "turretplates",
        "opp_turretplates", 
        "inhibitors",
        "opp_inhibitors",
        "damageToChampions",
        "dpm",
        "damageShare",
        "damageTakenPerMinute",
        "damageMitigatedPerMinute", 
        "wardsPlaced", 
        "wpm", 
        "wardsKilled", 
        "wcpm", 
        "controlWardsBought", 
        "visionScore",
        "vspm", 
        "totalGold", 
        "earnedGold",
        "earnedGpm", 
        "earnedGoldShare", 
        "goldSpent",
        "totalCs", 
        "minionKills", 
        "monsterKills", 
        "cspm", 
        "goldAt10",
        "xpAt10", 
        "csAt10", 
        "opp_goldAt10", 
        "opp_xpAt10",
        "opp_csAt10",
        "golddiffAt10",
        "xpdiffAt10",
        "csdiffAt10",
        "killsAt10",
        "assistsAt10",
        "deathsAt10",
        "opp_killsAt10",
        "opp_assistsAt10",
        "opp_deathsAt10", 
        "goldAt15",
        "xpAt15",
        "csAt15",
        "opp_goldAt15",
        "opp_xpAt15",
        "opp_csAt15",
        "golddiffAt15",
        "xpdiffAt15",
        "csdiffAt15",
        "killsAt15",
        "assistsAt15",
        "deathsAt15",
        "opp_killsAt15",
        "opp_assistsAt15",
        "opp_deathsAt15",
        "goldAt20",
        "xpAt20",
        "csAt20",
        "opp_goldAt20",
        "opp_xpAt20",
        "opp_csAt20",
        "golddiffAt20",
        "xpdiffAt20",
        "csdiffAt20",
        "killsAt20",
        "assistsAt20",
        "deathsAt20",
        "opp_killsAt20",
        "opp_assistsAt20",
        "opp_deathsAt20",
        "goldAt25",
        "xpAt25",
        "csAt25",
        "opp_goldAt25",
        "opp_xpAt25",
        "opp_csAt25",
        "golddiffAt25",
        "xpdiffAt25",
        "csdiffAt25",
        "killsAt25",
        "assistsAt25",
        "deathsAt25",
        "opp_killsAt25",
        "opp_assistsAt25",
        "opp_deathsAt25",
    
    # Data from mwrogue
        "championLevel",
        "opp_playerName",
        "opp_champion",
        "maxCsAdvantageOnLaneOpponent",
        "maxLevelLeadLaneOpponent",
        "killsNearEnemyTurret",
        "killsUnderOwnTurret",
        "soloKills",
        "damageDealtToTurrets",
        "firstTurretKilledTime",
        "stealthWardsPlaced",
        "controlWardsPlaced",
        "detectorWardsPlaced",
        "wardsKilledBefore20M",
        "controlWardTimeCoverageInRiverOrEnemyHalf",
        "wardsGuarded",
        "epicMonsterSteals",
        "jungleCsBefore10Minutes",
        "initialCrabCount",
        "scuttleCrabKills",
        "totalAllyJungleMinionsKilled",
        "totalEnemyJungleMinionsKilled",
        "earliestBaron",
        "completeSupportItemFirst",
        "saveAllyFromDeath",
        "totalDamageShieldedOnTeammates",
        "totalHealsOnTeammates",
        "totalTimeCCDealt",
        "effectiveHealAndShielding",
        "enemyChampionImmobilizations",
        "skillshotsHit",
        "skillshotsDodged",
        "item1",
        "item2",
        "item3",
        "item4",
        "item5",
        "item6",
        "rune1",
        "rune2",
        "rune3",
        "rune4",
        "rune5",
        "rune6",
        "featsOfStrength",
        "atakhanKills"
    ]
    return header

if __name__ == "__main__":
    tournament = [
        "LCK 2024 Spring", "LCK 2024 Spring Playoffs", "LCK 2024 Summer", "LCK 2024 Summer Playoffs", "LCK 2024 Regional Finals",
        # "LEC 2024 Winter", "LEC 2024 Winter Playoffs", "LEC 2024 Spring", "LEC 2024 Spring Playoffs", "LEC 2024 Summer", "LEC 2024 Summer Playoffs", "LEC 2024 Season Finals",
        # "LCS 2024 Spring", "LCS 2024 Spring Playoffs", "LCS 2024 Summer", "LCS 2024 Championship",
        # "PCS 2024 Spring", "PCS 2024 Spring Playoffs", "PCS 2024 Summer", "PCS 2024 Summer Playoffs",
        # "Worlds 2024 Play-In", "Worlds 2024 Main Event"
    ]
    gameIds = []
    datalist = []
    csvFilePath = "2024_LoL_esports_match_data_from_OraclesElixir.csv"
    oraclesCSV = pd.read_csv(csvFilePath, encoding="iso-8859-1", dtype=str)

    # gameIds = gameidGet(tournament[0])
    # oraclesData = oraclesDataGet(oraclesCSV, gameIds[0])

    # datalist.append(oraclesData[0])
    dataRow = 0
    doneRow = 0
    for i in range(len(tournament)):
        gameIds = gameidGet(tournament[i])
        dataRow += len(gameIds)
        for j in range(len(gameIds)):
            oraclesData = oraclesDataGet(oraclesCSV, gameIds[j])
            mwrogueData = mwrogueDataGet(gameIds[j])
            for k in range(10):
                gameData = oraclesData[k] + mwrogueData[k]
                datalist.append(gameData)
            doneRow += 1
            print(f"{doneRow} / {dataRow}")

    df = pd.DataFrame(datalist, columns=datasetHeader())

    file_path = "gameData.csv"
    if os.path.exists(file_path):
        try:
            existing_df = pd.read_csv(file_path)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.to_csv(file_path, index=False)
        except ValueError:
            df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, index=False)
