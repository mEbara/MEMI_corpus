import os, sys, re, json
import codecs
from collections import defaultdict
import pathlib
import textwrap
import random

from openai import OpenAI
import replicate

import util

config = util.load_json('config.json') # Set API, instruction prompt, model version

def run_GPT(scenario, tree, annotate, context_messages, game_text, options, language, seed):
    client = OpenAI(api_key=config["GPT"]["API"])
    #model_version = "gpt-4o-2024-08-06"  #'gpt-3.5-turbo-1106" "gpt-3.5-turbo-0125"
    model_version = config["GPT"]["Model version"] # gpt-4o-2024-11-20
    
    choice_text = util.make_options_text(options, language) ## options' texts

    ## if you need with contexts, please comment out below
    #context_messages = []
    ###

    if len(context_messages) == 0:
        system_text = util.get_role_text(scenario['node_1'][language], language) + config["GPT"]["Instruction prompt"] ## SYSTEM PROMPT
        context_messages = [{
                 'role': 'system', 
                 'content': system_text,
                 }]

    messages = [{'role': 'user', 
                 'content': f'{game_text}{choice_text}'
                 }]
    

    context_messages.extend(messages)   # append previous context
    
    response = client.chat.completions.create(model=model_version,
                                              messages=context_messages,
                                              temperature=1,
                                              top_p=1,
                                              seed=seed
                                              )
    response_message = response.choices[0].message.content
    #output = res['choices'][0]['message']['content']

    output = response_message

    #answer = re.findall(r'([A-Z])', output)
    answer = re.findall(r'([1-9])', output)

    # outputをcontextに追加
    context_messages.append({
                            'role': 'assistant',
                            'content': output,
    })    


    return output, answer, choice_text, context_messages


def run_llama(scenario, tree, annotate, context_messages, game_text, options, language,seed):
    os.environ["REPLICATE_API_TOKEN"] = config["LLAMA"]["API"]
    instruction_prompt = util.get_role_text(scenario['node_1'][language], language) + config["LLAMA"]["Instruction prompt"] ## SYSTEM PROMPT
    model_version = config["LLAMA"]["Model version"]
   
    # Create input text
    choice_text = util.make_options_text(options, language) # options
    user_input = f'{game_text}{choice_text}'
    prompt = build_prompt_4_llama(instruction_prompt, context_messages, user_input)

    output = replicate.run(
        model_version,
        input={
            "top_p": 1,
            "temperature": 1,
            "seed": seed,
            "system_prompt": instruction_prompt,
            "prompt": prompt,
            "max_new_tokens": 200
        }
    )

    response = "".join(output).replace('\n', '')
    answer = re.findall(r'([1-9]:)', response)

    # Save chat history
    context_messages.append({"user": user_input, "assistant": response})
    return response, answer, choice_text, context_messages


def build_prompt_4_llama(instruction_prompt, history:list, user_input) -> str: 
    prompt = f"<<SYS>>\n{instruction_prompt}\n<</SYS>>\n\n"
    for turn in history:
        prompt += f"[INST] {turn['user']} [/INST] {turn['assistant']}\n"
    prompt += f"[INST] {user_input} [/INST]"
    return prompt

def random_choice(options: dict, language): # Generate randomized decision
    keys = '123456789'
    answer = keys[random.randrange(len(options))]
    choice_text = util.make_options_text(options, language)
    return answer, choice_text