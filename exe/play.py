import os, sys, re, json
import codecs
from collections import defaultdict

import util as util, models as models

from tap import Tap


class Args(Tap):
    scenarioID: str = "Q38"
    play_mode: str = "Interaction" # Interaction or GPT or LLAMA or RANDOM
    output_dir: str = "outputs"
    language: str = "EN" # EN or JA
    order: str = "-1"
    patient_status: str = "0_0_0_0"

class Interaction_mode:
    def __init__(self, args: Args):
        self.args: Args = args
        self.scenarioID  = args.scenarioID

        self.scenario, self.tree, self.annotation = util.load_game(self.scenarioID)
        self.Trajectory    : list = ['node_1']
        self.choice        : list = []
        self.language      : str  = args.language
        self.output_dir    : str  = args.output_dir
        self.order         : str  = args.order
        self.patient_status:list  = util.get_patient_status(args.scenarioID, args.patient_status, self.language)

        self.chat_history = dict() 

    def run(self): # Interaction mode
        cnt = 0
        while True:

            if self.tree[self.Trajectory[-1]]['type'] == 'box':

                if len(self.tree[self.Trajectory[-1]]['children']) == 1:
                    previous = util.display_game_text(self.Trajectory[-1], self.scenario[self.Trajectory[-1]][self.language], self.patient_status, self.language)
                    
                    self.chat_history[self.Trajectory[-1]] ={"input":"", "answer":""}
                    self.chat_history[self.Trajectory[-1]]["input"] = util.display_game_text(self.Trajectory[-1], self.scenario[self.Trajectory[-1]][self.language], self.patient_status, self.language)
                    self.chat_history[self.Trajectory[-1]]["answer"] = [self.tree[self.Trajectory[-1]]['children'][0], "NEXT"]

                    self.Trajectory.append(self.tree[self.Trajectory[-1]]['children'][0])
                    print(previous)                    
               
                    continue
        
                else:
                    scenario_text = util.display_game_text(self.Trajectory[-1], self.scenario[self.Trajectory[-1]][self.language], self.patient_status, self.language)
                    options = util.make_options(self.tree[self.Trajectory[-1]]['children'], self.Trajectory, self.scenario, self.language)
                    options_text = util.make_options_text(options, self.language)

                    self.chat_history[self.Trajectory[-1]] ={"input":"", "options":"", "answer":""}
                    self.chat_history[self.Trajectory[-1]]["input"] = util.display_game_text(self.Trajectory[-1], self.scenario[self.Trajectory[-1]][self.language], self.patient_status, self.language)
                    self.chat_history[self.Trajectory[-1]]["options"] = options_text

                    print('Q.\n',f'{scenario_text}{options_text}')

                    action = str(input())

                    if action in options:
                        self.Trajectory.append(options[action]['index'])
                        print(f"{action}:{options[action]['text']}")
                        print('--------------------------------------------------')
                        self.chat_history[self.Trajectory[-2]]["answer"] = [self.Trajectory[-1], action, options[action]['text']]

                    else:
                        here = self.Trajectory[-1]
                        self.Trajectory.append(here)

            elif self.tree[self.Trajectory[-1]]['type'] == 'edge':
                self.Trajectory.append(self.tree[self.Trajectory[-1]]['children'][0])                                        
                                                 
            if 'END' in self.tree[self.Trajectory[-1]]['type']:
                print(util.display_game_text(self.Trajectory[-1], self.scenario[self.Trajectory[-1]][self.language], self.patient_status, self.language))
                print('--------------------------------------------------')
                self.chat_history[self.Trajectory[-1]] = {"input":self.scenario[self.Trajectory[-1]][self.language], 
                                                          "answer":"END",
                                                          "output":"NONE"}
                self.chat_history["Trajectory"] = self.Trajectory
                util.save_output(self.output_dir, self.order, "interaction", self.scenarioID, self.chat_history, self.patient_status, self.language)
                break

class LLM_mode:
    def __init__(self, args: Args):
        self.args: Args = args
        
        self.model : str = args.play_mode # GPT, LLAMA
        self.seed  : int = int(args.order[1:])

        # setup
        self.output_dir    : str  = args.output_dir
        self.order         : str  = args.order
        self.scenarioID    : str  = args.scenarioID
        self.scenario, self.tree, self.annotation = util.load_game(args.scenarioID)
        self.Trajectory    : list = ['node_1']
        self.choice        : list = []
        self.language      : str  = args.language
        self.patient_status: list = util.get_patient_status(args.scenarioID, args.patient_status, self.language)

        self.chat_history  : dict = dict() # save chat history

        self.error_cnt = 0   # count errors

    def run(self): # LLMs mode
        cnt = 0
        flag = False
        previous  = ''
        context_messages = []
        while True:
            if self.tree[self.Trajectory[-1]]['type'] == 'box':
 
                node_text = util.display_game_text(self.Trajectory[-1], self.scenario[self.Trajectory[-1]][self.language], self.patient_status, self.language)
                print(node_text)

                if len(self.tree[self.Trajectory[-1]]['children']) == 1:
                    print('--------------------------------------------------\n')
                    previous = self.scenario[self.Trajectory[-1]][self.language]
                    self.Trajectory.append(self.tree[self.Trajectory[-1]]['children'][0])                    
                    continue    

                else:
                    if len(previous) > 0:
                        game_text = util.display_game_text(self.Trajectory[-1], previous, self.patient_status, self.language) + util.display_game_text(self.Trajectory[-1], self.scenario[self.Trajectory[-1]][self.language], self.patient_status, self.language)
                        previous = ''
                    else:
                        game_text = util.display_game_text(self.Trajectory[-1], self.scenario[self.Trajectory[-1]][self.language], self.patient_status, self.language)
                    options = util.make_options(self.tree[self.Trajectory[-1]]['children'], self.Trajectory, self.scenario, self.language)

                    
                    if self.model == 'GPT':
                        output, answer, choice_text, context_messages= models.run_GPT(                                                                            
                                                                              self.scenario, 
                                                                              self.tree, 
                                                                              self.annotation, 
                                                                              context_messages, 
                                                                              game_text, options,
                                                                              self.language,
                                                                              self.seed)
                        
                    elif self.model == 'LLAMA':
                        output, answer, choice_text, context_messages= models.run_llama(
                                                                                 self.scenario,
                                                                                 self.tree,
                                                                                 self.annotation,
                                                                                 context_messages,
                                                                                 game_text,
                                                                                 options,
                                                                                 self.language,
                                                                                 self.seed)

                    elif self.model == 'RANDOM':
                        output, choice_text = models.random_choice(options, self.language)
                        answer = output
                        context_messages = []

                    if len(answer) > 0:
                        ans = re.findall(r'([1-9])', answer[0])
                        action = ans[0]
                    else: # when the answer is invalid
                        action = 'Z'


                    print(choice_text, action) # Options and answer
                    print("MODEL'S OUTPUT:\n「", output, "　」\n")
                    print('--------------------------------------------------\n')

                    if action in options:
                        self.chat_history[self.Trajectory[-1]] = {"input":game_text}
                        self.chat_history[self.Trajectory[-1]]["options"] = choice_text
                        self.chat_history[self.Trajectory[-1]]["answer"] = [options[action]['index'], action, self.scenario[options[action]['index']][self.language]]
                        self.chat_history[self.Trajectory[-1]]["output"] = output
                        
                        self.Trajectory.append(options[action]['index'])

                    else:
                        here = self.Trajectory[-1]
                        self.Trajectory.append(here)
                        self.error_cnt += 1

                        self.chat_history[self.Trajectory[-1]+'-'+str(self.error_cnt)] = {"input":game_text}
                        self.chat_history[self.Trajectory[-1]+'-'+str(self.error_cnt)]["options"] = choice_text
                        self.chat_history[self.Trajectory[-1]+'-'+str(self.error_cnt)]["answer"] = ["ERROR", action]
                        self.chat_history[self.Trajectory[-1]+'-'+str(self.error_cnt)]["output"] = output

                        if self.error_cnt >= 5:
                            break


            elif self.tree[self.Trajectory[-1]]['type'] == 'edge':
                self.Trajectory.append(self.tree[self.Trajectory[-1]]['children'][0])
                                                                                            
            if 'END' in self.tree[self.Trajectory[-1]]['type'] or self.error_cnt >= 5:
                print(self.scenario[self.Trajectory[-1]][self.language])
                print('\n--------------------------------------------------')
                print('CONTEXT:\t', context_messages)
                print('--------------------------------------------------')
                
                # save the model's output
                self.chat_history[self.Trajectory[-1]] = {"input":self.scenario[self.Trajectory[-1]][self.language], 
                                                          "answer":"END",
                                                          "output":"NONE"}
                self.chat_history["Trajectory"] = self.Trajectory
                util.save_output(self.output_dir, self.order, self.model, self.scenarioID, self.chat_history, self.patient_status, self.language)
                break
      

def main(args: Args):
    if args.play_mode == "Interaction":
        play = Interaction_mode(args=args)
    else:
        play = LLM_mode(args=args)
        print(args.play_mode, args.order, args.scenarioID)
        print('--------------------------------------------------')
    play.run()

if __name__ == "__main__":
    args = Args().parse_args()
    main(args)