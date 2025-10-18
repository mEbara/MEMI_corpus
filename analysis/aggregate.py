import os, json
import datetime
import pandas as pd


key = ["RFA", "BAN", "JST", "CM"]

def get_filelist(path: str, key: str) -> list:
    filelist = [item for item in os.listdir(path) if key in item]
    filelist.sort()
    return filelist

def get_scenariolist(path: str) -> list:
    listdir = [item for item in os.listdir(path) if 'Q' in item]
    filelist = sorted(listdir, key=lambda x: int(x.split('.')[0][1:]))
    return filelist

def load_json(path: str) -> dict:
    with open(path, mode='r', encoding='UTF-8') as f:
        j = json.load(f)
    return j

def save_json(path: str, save_dict: dict) -> None:
    with open(path, mode='w', encoding='UTF-8') as f:
        json.dump(save_dict, f, ensure_ascii=False, indent=2)

def agg_observed_violation(trajectory: list, ann: dict) -> list:
    violations: list = [0]*4 # RFA, BAN, JST, CM
    for item in  trajectory:            
        if item in ann: # Aggregate only the annotated edges
            for i in range(len(key)):
                if ann[item][key[i]] != [0]:
                    violations[i] += len(ann[item][key[i]])
    return violations

#######################################################################

result = []
scenario_stats = load_json("scenario_stats.json")
respondents = get_filelist("../exe/outputs", "-")

for r in respondents:
    response_files = get_scenariolist(f"../exe/outputs/{r}")
    order = r.split('-')[-1]
    name = r.split('-')[0]
    data = {"Subject":f"{name}-{order}"}
    for scenarioID in response_files:
        response = load_json(f"../exe/outputs/{r}/{scenarioID}")["Trajectory"]
        ann = load_json(f"../exe/data/annotation/{scenarioID}")

        observed :int   = agg_observed_violation(response, ann)
        max_vl   :float = scenario_stats[scenarioID]["max"]

        Escore   :float = max_vl - sum(observed)
        data[scenarioID] = Escore
    result.append(data)

result_df: pd.DataFrame = pd.DataFrame(result)

filename :str = str(datetime.date.today()) # fill name as you like
result_df.to_csv(f"{filename}.csv")