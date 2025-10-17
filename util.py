import os, re, json
import pandas as pd
import codecs
import os, sys, re, json, random, datetime
import codecs
from pathlib import Path
from collections import defaultdict
import util


def load_json(path: str) -> dict:
    with open(path, mode='r', encoding='UTF-8') as f:
        j = json.load(f)
    return j

def listup_games(path):
    game_list = sorted(os.listdir(path + '/scenario'))
    for item in game_list:
        print(item)

def load_game(game):
    path = "corpus"
    scenariofile = f"{game}.json"

    with open(os.path.join(path, "scenario", scenariofile), mode="r", encoding="UTF-8") as f:
        scenario = json.load(f)
    with open(os.path.join(path, "tree", scenariofile), mode="r", encoding="UTF-8") as f:
        tree = json.load(f)
    with open(os.path.join(path, "annotation", scenariofile), mode="r", encoding="UTF-8") as f:
        annotation = json.load(f)
    return scenario, tree, annotation

def save_output(output_dir:str, order: str, model: str, scenarioID:str, chat_history: dict, patient_status: list, language:str) -> None:
    if model == "interaction":
        model = "Human"
        info = {"Model version": "Human"}
    else:
        info =  {k: v for k, v in load_json('config.json')[model].items() if k != 'API'} #config.jsonで設定を管理

    info["Patient status"] = patient_status
    chat_history["Info"] = info # add "model version", "system prompt", "patient param"

    today:str = str(datetime.date.today())
    output_dir_path:str = f"{output_dir}/{model}-{today}{order}"
    Path(output_dir_path).mkdir(exist_ok=True)  # make today's directory
    print('The output is saved ->', f"{os.getcwd()}/{output_dir_path}/{scenarioID}.json")
    
    with open(f"{output_dir_path}/{scenarioID}.json", 'w') as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)


####################### Agent's role for model ###################################
def get_role_text(rootnode_text: str, language: str) -> str:
    if language == "JA":
        role_text_find: list = re.findall(r'(あなたは.*です)', rootnode_text.split('。')[0])
        if len(role_text_find) > 0:
            role_text = role_text_find[0] + '。\n'
    elif language == "EN":
        if "START" in rootnode_text:
            print('Rootnode text:', rootnode_text.split('#')[0])
            role_text_find: list = re.findall(r'(You are .*)', rootnode_text.split('.')[0])
            if len(role_text_find) > 0:
                role_text = role_text_find[0].replace("#", "") + '.\n '
                print('role_text', role_text)
    else:
        print('ERROR something wrong at get_role_text in util')
        role_text = ''
    return role_text

def display_game_text(node: str, game_text: str, patient_data:list, language: str) -> str:
    if node == 'node_1':
        if language == "JA":
            norm_game_text = '-START-\n' + '。'.join(game_text.split('。')[1:])
            new_game_text = get_patient_text(norm_game_text, patient_data, language)
        elif language == "EN":
            norm_game_text = '-START-\n' + '.'.join(game_text.split('.')[1:]).replace("#", "")
            new_game_text = get_patient_text(norm_game_text, patient_data, language)
    else:
        new_game_text = game_text
    
    if language == "JA":
        data = new_game_text.replace('。', '。\n').replace('。\n」', '。」\n')
    elif language == "EN":
        data = new_game_text.replace('.', '.\n').replace('.\n"', '."\n')

    return data

def trajectory_count(Trajectry: list) -> dict:
    trajectory_dict = dict()
    for item in Trajectry:
        if "edge" in item:
            if item in trajectory_dict:
                trajectory_dict[item] += 1
            else:
                trajectory_dict[item] = 1
    return trajectory_dict

def make_options(tree_children: list, Trajectory: list, scenario: dict, language: str) -> dict[str:str]:
    keys = '123456789'
    options = dict()
    cnt = 0
    trajectory_dict = trajectory_count(Trajectory)

    shuffled_tree_children = random.sample(tree_children, len(tree_children)) #選択肢の順番をシャッフルする
    for item in shuffled_tree_children:
        if trajectory_dict.get(item,0) < 2: # option at most twice
            options[keys[cnt]] = {'index': item, 'text': scenario[item][language].replace('\\n', '')}
            cnt += 1
    return options

def make_options_text(options: dict[str:{str:str}], language: str) -> str:
    options_text = [v[0]+':'+v[1]['text'] for i,v in enumerate(options.items())]
    if language == 'EN':
        text = '\n' + '\n'.join(options_text) + '\n\nYour answer is '
    elif language == 'JA':
        text = '\n' + '\n'.join(options_text) + '\n\nあなたの答えは、'
    return text


lex = {"Unknown":{"JA":"None", "EN":"None"},"None":{"JA":"None", "EN":"None"}, 
       "Male":{"JA":"男性", "EN":"male"}, "Female":{"JA":"女性", "EN":"female"},
       "White": {"JA":"白人", "EN":"white"}, "Black":{"JA":"黒人", "EN":"black"},
       "Asian":{"JA":"アジア人", "EN":"asian"}, "Hispanic":{"JA":"ヒスパニック系","EN":"hispanic"},
       "MD":{"JA":"精神障害", "EN":"a mental disorder"}, "DD":{"JA":"発達障害", "EN":"a neurodevelopmental disorder"},
       "DM":{"JA":"糖尿病","EN":"diabetes"}, "STD":{"JA":"性感染症", "EN":"sexually transmitted infections"},
       }

def get_patient_status(gamefile:str, status_text:str, language: str) -> list:
    status_data  = status_text.replace('\n', '').split('_')
    if status_data[0] == '0':
        patient_data = status_data
    else:
        patient_data = [status_data[0]] + [lex[x][language] for x in status_data[1:]]
    print('patient data:', patient_data)     # 16_Male_White_DD
    return patient_data


def get_patient_text(scenario_text: str, patient_data: list, language: str) -> str:
    status_list = ["Age","Gender", "Race","Medical history"]
    nan = set(["None", "Unknown"])
    
    if patient_data[0] == '0':
        scenario_text = scenario_text.replace("@", "").replace("#", "")

    else:
        if language == "JA" or language == "JP": # ['19', '男性', '黒人', 'None', '肥満', 'None', 'None']
            original_A = re.findall(r'(患者は.*歳.*性です。)', scenario_text)
            original_B = re.findall(r'(妊婦は.*歳女性です。)', scenario_text)
            original = original_A + original_B

            if len(original) > 0:

                original_text = original[0]

                if all(x == 'None' for x in patient_data[:3] + patient_data[4:5]):
                    patient_text = ''
                else:
                    age:str = 'None' if patient_data[0] == 'None' else patient_data[0] + '歳'
                    patient_text = f'患者は{age}{patient_data[2]}{patient_data[1]}です。'

                if patient_data[3] != 'None': # Medical history
                    patient_text += f'なお、その患者は、{patient_data[3]}の既往があるそうです。'

                if len(original_B) > 0:
                    patient_text = patient_text.replace('患者', '妊婦')

                scenario_text = scenario_text.replace(original_text, patient_text).replace('None', '')

        elif language == "EN": # ['19', '男性', '黒人', 'None', '肥満', 'None', 'None']
            original = re.findall(r'(@.*@)', scenario_text)

            if len(original) > 0:

                original_text = original[0]

                if all(x == 'None' for x in patient_data[:3] + patient_data[4:5]):
                    patient_text = ''
                else:
                    age          :str = " a None" if patient_data[0] in nan else f" a {patient_data[0]}-year-old"
                    if patient_data[0] in set(["8","18","80","81","82","83","84","85","86","87","88","89"]):
                        age = age.replace(' a ', ' an ')

                    race         :str = " None" if patient_data[2] in nan else f" {patient_data[2]}"
                    sex          :str = " individual" if patient_data[1] in nan else f" {patient_data[1]}"
                    patient_text :str = f"The patient is{age}{race}{sex}."

                if patient_data[3] != 'None': # Medical history
                    patient_text += f'Incidentally, the patient reportedly has a history of {patient_data[3]}.'

                scenario_text = scenario_text.replace(original_text, patient_text).replace(' None', '')

    return scenario_text