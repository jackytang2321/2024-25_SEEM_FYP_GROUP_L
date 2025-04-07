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
        "gameId", #1
        "league", #2
        "year", #3
        "split", #4
        "playoffs", #5
        "date", #6
        "game", #7
        "patch", #8
        "participantId", #9
        "side", #10
        "position", #11
        "playerName", #12
        "teamName", #13
        "champion", #14
        "ban1", #15
        "ban2", #16
        "ban3", #17
        "ban4", #18
        "ban5", #19
        "opp_ban1", #20
        "opp_ban2", #21
        "opp_ban3", #22
        "opp_ban4", #23
        "opp_ban5", #24
        "pick1", #25
        "pick2", #26
        "pick3", #27
        "pick4", #28
        "pick5", #29
        "opp_pick1", #30
        "opp_pick2", #31
        "opp_pick3", #32
        "opp_pick4", #33
        "opp_pick5", #34
        "gamelength", #35
        "win", #36
        "kills", #37
        "deaths", #38
        "assists", #39
        "teamKills", #40
        "teamDeaths", #41
        "doublekills", #42
        "triplekills", #43
        "quadrakills", #44
        "pentakills", #45
        "firstblood", #46
        "firstbloodKill", #47
        "firstbloodAssist", #48
        "firstbloodVictim", #49
        "teamKpm", #50
        "ckpm", #51
        "firstdragon", #52
        "dragons", #53
        "opp_dragons", #54
        "elementalDrakes", #55
        "opp_elementalDrakes", #56
        "infernals", #57
        "mountains", #58
        "clouds", #59
        "oceans", #60
        "chemtechs", #61
        "hextechs", #62
        "elders", #63
        "opp_elders", #64
        "firstherald", #65
        "heralds", #66
        "opp_heralds", #67
        "voidgrubs", #68
        "opp_voidgrubs", #69
        "firstBaron", #70
        "barons", #71
        "opp_barons", #72
        "firsttower", #73
        "towers", #74
        "opp_towers", #75
        "firstMidTower", #76
        "firstToThreeTowers", #77
        "turretplates", #78
        "opp_turretplates", #79
        "inhibitors", #80
        "opp_inhibitors", #81
        "damageToChampions", #82
        "dpm", #83
        "damageShare", #84
        "damageTakenPerMinute", #85
        "damageMitigatedPerMinute", #86
        "wardsPlaced", #87
        "wpm", #88
        "wardsKilled", #89
        "wcpm", #90
        "controlwardsBought", #91
        "visionscore", #92
        "vspm", #93
        "totalgold", #94
        "earnedGold", #95
        "earnedGpm", #96
        "earnedGoldShare", #97
        "goldSpent", #98
        "totalCs", #99
        "minionKills", #100
        "monsterKills", #101
        "cspm", #102
        "goldAt10", #103
        "xpAt10", #104
        "csAt10", #105
        "opp_goldAt10", #106
        "opp_xpAt10", #107
        "opp_csAt10", #108
        "golddiffAt10", #109
        "xpdiffAt10", #110
        "csdiffAt10", #111
        "killsAt10", #112
        "assistsAt10", #113
        "deathsAt10", #114
        "opp_killsAt10", #115
        "opp_assistsAt10", #116
        "opp_deathsAt10", #117
        "goldAt15", #118
        "xpAt15", #119
        "csAt15", #120
        "opp_goldAt15", #121
        "opp_xpAt15", #122
        "opp_csAt15", #123
        "golddiffAt15", #124
        "xpdiffAt15", #125
        "csdiffAt15", #126
        "killsAt15", #127
        "assistsAt15", #128
        "deathsAt15", #129
        "opp_killsAt15", #130
        "opp_assistsAt15", #131
        "opp_deathsAt15", #132
        "goldAt20", #133
        "xpAt20", #134
        "csAt20", #135
        "opp_goldAt20", #136
        "opp_xpAt20", #137
        "opp_csAt20", #138
        "golddiffAt20", #139
        "xpdiffAt20", #140
        "csdiffAt20", #141
        "killsAt20", #142
        "assistsAt20", #143
        "deathsAt20", #144
        "opp_killsAt20", #145
        "opp_assistsAt20", #146
        "opp_deathsAt20", #147
        "goldAt25", #148
        "xpAt25", #149
        "csAt25", #150
        "opp_goldAt25", #151
        "opp_xpAt25", #152
        "opp_csAt25", #153
        "golddiffAt25", #154
        "xpdiffAt25", #155
        "csdiffAt25", #156
        "killsAt25", #157
        "assistsAt25", #158
        "deathsAt25", #159
        "opp_killsAt25", #160
        "opp_assistsAt25", #161
        "opp_deathsAt25", #162
    
    # Data from mwrogue
        "championLevel", #163
        "maxCsAdvantageOnLaneOpponent", #164
        "maxLevelLeadLaneOpponent", #165
        "killsNearEnemyTurret", #166
        "killsUnderOwnTurret", #167
        "soloKills", #168
        "damageDealtToTurrets", #169
        "firstTurretKilledTime", #170
        "stealthWardsPlaced", #171
        "controlWardsPlaced", #172
        "detectorWardsPlaced", #173
        "wardsKilledBefore20M", #174
        "controlWardTimeCoverageInRiverOrEnemyHalf", #175
        "wardsGuarded", #176
        "epicMonsterSteals", #177
        "jungleCsBefore10Minutes", #178
        "initialCrabCount", #179
        "scuttleCrabKills", #180
        "totalAllyJungleMinionsKilled", #181
        "totalEnemyJungleMinionsKilled", #182
        "completeSupportItemFirst", #183
        "saveAllyFromDeath", #184
        "totalDamageShieldedOnTeammates", #185
        "totalHealsOnTeammates", #186
        "totalTimeCCDealt", #187
        "effectiveHealAndShielding", #188
        "enemyChampionImmobilizations", #189
        "skillshotsHit", #190
        "skillshotsDodged", #191
        "item1", #192
        "item2", #193
        "item3", #194
        "item4", #195
        "item5", #196
        "item6", #197
        "rune1", #198
        "rune2", #199
        "rune3", #200
        "rune4", #201
        "rune5", #202
        "rune6", #203
        "featsOfStrength", #204
        "atakhanKills" #205
    ]
    return header

if __name__ == "__main__":
    finishedTournament = [
        "LCK 2024 Spring", "LCK 2024 Spring Playoffs", "LCK 2024 Summer", "LCK 2024 Summer Playoffs", "LCK 2024 Regional Finals"
    ]

    tournament = [
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