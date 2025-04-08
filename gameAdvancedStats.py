from mwrogue.esports_client import EsportsClient
from bs4 import BeautifulSoup
import json
import pandas as pd
import datetime
import os
import math

def datasetHeader():
    header = [
        # Game Basic Info
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
        "opp_playerName",
        "opp_champion",

        # Advanced Stats
        "kda",
        "killParticipation",
        "killsImpact",
        "solokillRatio",
        "damagePerGold",
        "damageEfficiency",
        "earlyGameStrength",
        "efficientVisionScore",
        "visionControl",
        "visionThreat",
        "earliestBaronEndRate",
        "objectiveTimeRatio",
        "ccEfficiency",
        "saveEfficiencyRatio",
        "survivability"
    ]
    return header

def advancedStats(df):
    datalist = pd.DataFrame(columns=datasetHeader())

    for i in range(len(df)):
        target_df = df.iloc[i]
        opp_df = df[(df["gameId"] == target_df["gameId"]) & (df["playerName"] == target_df["opp_playerName"])]
        # team_df = df[(df["gameId"] == target_df["gameId"])]
        # team_df = team_df.reset_index(drop=True)
        newdata = []

        # Game Basic Info
        for j in range(14):
            newdata.append(target_df[i][j])
        for j in range(163, 165):
            newdata.append(target_df[i][j])

        # Related Elements
        goldDiffAtEnd = target_df["totalGold"] - opp_df["totalGold"]

        # Advanced Stats Calculation
        kda = (target_df["kills"] + target_df["assists"]) / target_df["deaths"].apply(lambda x: max(x, 1))
        killParticipation = (target_df["kills"] + target_df["assists"]) / target_df["teamKills"]
        killsImpact = (killParticipation * goldDiffAtEnd) / (target_df["gameLength"] * target_df["teamDeaths"])
        solokillRatio = target_df["soloKills"] / target_df["kills"]
        damagePerGold = target_df["damageToChampions"] / target_df["totalGold"]
        damageEfficiency = (target_df["damageToChampions"] / (target_df["kills"] + target_df["assists"])) / (target_df["gameLength"] / target_df["deaths"].apply(lambda x: max(x, 1)))
        efficientVisionScore = (target_df["wardsPlaced"] + target_df["wardsKilled"]) * (target_df["visionScore"] / df["visionScore"].mean()) / \
            (target_df["teamKills"] + target_df["dragons"] + target_df["voidgrubs"] + target_df["heralds"] + target_df["barons"] + target_df["elders"])
        earlyGameStrength = ((target_df["golddiffAt15"] + target_df["xpdiffAt15"]) / 100 + target_df["csdiffAt15"] + target_df["killsAt15"] + target_df["assistsAt15"] + target_df["turretplates"]) / \
            ((df["golddiffAt15"].mean() + df["xpdiffAt15"]).mean() / 100 + df["csdiffAt15"].mean() + df["killsAt15"].mean() + df["assistsAt15"].mean() + df["turretplates"].mean())
        '''
        if target_df["golddiffAt15"] > 0:
            earlyLeadToWinConversionRate = goldDiffAtEnd / target_df["golddiffAt15"]
        else:
            earlyLeadToWinConversionRate = None
        '''
        if target_df["earliestBaron"] != None and target_df["win"] == 0:
            earliestBaronEndRate = -1 * (target_df["gameLength"] - target_df["earliestBaron"]) / (df["gameLength"].mean() - df["earliestBaron"].mean())
        elif target_df["earliestBaron"] != None and target_df["win"] == 1:
            earliestBaronEndRate = (target_df["gameLength"] - target_df["earliestBaron"]) / (df["gameLength"].mean() - df["earliestBaron"].mean())
        else:
            earliestBaronEndRate = None
        saveEfficiencyRatio = (target_df["saveAllyFromDeath"] + target_df["effectiveHealAndShielding"] / 1000) / opp_df["teamKills"]
        ccEfficiency = target_df["totalTimeCCDealt"] * killParticipation / target_df["deaths"].apply(lambda x: max(x, 1))
        objectiveTimeRatio = target_df["voidgrubs"] + target_df["dragons"] * 1.25 + target_df["heralds"] * 1.5 + target_df["barons"] * 2.5 + target_df["elders"] * 3
        survivability = ((target_df["damageTakenPerMinute"] + target_df["damageMitigatedPerMinute"]) * target_df["gameLength"] / 60) / target_df["deaths"].apply(lambda x: max(x, 1))
        visionControl = target_df["wardsKilled"] / target_df["controlWardsPlaced"].apply(lambda x: max(x, 1))
        if target_df["controlWardTimeCoverageInRiverOrEnemyHalf"] != None:
            visionThreat = (target_df["controlWardTimeCoverageInRiverOrEnemyHalf"] * target_df["controlWardsPlaced"].apply(lambda x: max(x, 1))) / target_df["gameLength"]
        else:
            visionThreat = 0

        # Advanced Stats Output
        newdata.append(kda)
        newdata.append(killParticipation)
        newdata.append(killsImpact)
        newdata.append(solokillRatio)
        newdata.append(damagePerGold)
        newdata.append(damageEfficiency)
        newdata.append(earlyGameStrength)
        # newdata.append(earlyLeadToWinConversionRate)
        newdata.append(efficientVisionScore)
        newdata.append(visionControl)
        newdata.append(visionThreat)
        newdata.append(earliestBaronEndRate)
        newdata.append(objectiveTimeRatio)
        newdata.append(ccEfficiency)
        newdata.append(saveEfficiencyRatio)
        newdata.append(survivability)
        
        datalist = pd.concat([datalist, pd.DataFrame([newdata], columns=datasetHeader)], ignore_index=True)
    return datalist

if __name__ == "__main__":
    file_path = "gameData.csv"
    gameData_df = pd.read_csv(file_path)
    advancedData_df = advancedStats(gameData_df)
    
    file_path = "gameAdvancedStats.csv"
    if os.path.exists(file_path):
        try:
            existing_df = pd.read_csv(file_path)
            combined_df = pd.concat([existing_df, advancedData_df], ignore_index=True)
            combined_df.to_csv(file_path, index=False)
        except ValueError:
            advancedData_df.to_csv(file_path, index=False)
    else:
        advancedData_df.to_csv(file_path, index=False)
