# coding: UTF-8
#from bert_juman import BertWithJumanModel
import numpy as np
import os
import sys
import MeCab
import time
import pandas as pd
import json
import math
import subprocess
import pprint as pp
from threading import Thread
from queue import Queue, Empty

#from eval_pipeline import multi_pipeline
#from eval_pipeline.multi_pipeline import pipeline
#from eval_pipeline import reset_util

import torch
from transformers import BertModel, BertForNextSentencePrediction
#from transformers.tokenization_bert_japanese import BertJapaneseTokenizer as BertTokenizer
from transformers import BertJapaneseTokenizer as BertTokenizer

def get_duration(path = "C:/Users/hirok/OneDrive/Desktop/SST_v2/SST2020/Roleplay/audio_duration.txt", subtract_sec = 1.0):
    
    with open(path) as f:
        
        duration_str = f.read()
        duration_float = float(duration_str)
    
    duration_float = duration_float - subtract_sec
    
    if duration_float < 0:
        duration_float = 0.1
    
    return duration_float
        


#path_w = r'C:\Users\hirok\OneDrive\Desktop\Greta_googletts\1.src\bin\Examples\DemoEN\reseponse\generate.xml'
path_w = r'C:\Users\hirok\OneDrive\Desktop\Greta_ASAP\greta_ASAP_ASR_SST_20230710\greta_ASAP_ASR_SST_20230710\greta_ASAP_googleTTS\bin\Examples\DemoEN\reseponse\generate.xml'

s1 = "<?xml version=\"1.0\" encoding=\"shift_jis\" ?>\n"
s2 = "<fml-apml>\n"
s3="<bml>\n"
s4="<speech id=\"s1\" language=\"ja-JP\" start=\"0.0\" text=\"\" type=\"SAPI4\" voice=\"cerevoice\" xmlns=\"\">\n"
s5="\n"
s6="</speech>\n"
s7="</bml>\n"
s8="</fml-apml>"



subprocess.call("record_copy.bat", shell=True)
#subprocess.call("record_copy_cam2.bat", shell=True)

## Feedback ##

utter="計算を開始します。"
s5=utter+"\n"

with open(path_w, mode="w") as f:
  f.write(s1)
  f.write(s2)
  f.write(s3)
  f.write(s4)
  f.write(s5)
  f.write(s6)
  f.write(s7)
  f.write(s8)
          
#subprocess.call("dummy.bat", shell=True)
#subprocess.call("dummy.bat", shell=True)

# feedback option1: slow
#results = multi_pipeline.pipeline(task_name)
#pp.pprint(results)

# feedback option2: faster
subprocess.call("python eval_pipeline\multi_pipeline.py FAVOR", shell=True)



json_open_feedback = open('result_for_viewer/result.json', 'r')
json_load_feedback = json.load(json_open_feedback)


feedback_pos=json_load_feedback["PositiveComment"]
feedback_neg=json_load_feedback["NegativeComment"]
  

# utter="ではフィードバックです。"+feedback_pos+feedback_neg
# s5=utter+"\n"


# with open(path_w, mode="w") as f:
#   f.write(s1)
#   f.write(s2)
#   f.write(s3)
#   f.write(s4)
#   f.write(s5)
#   f.write(s6)
#   f.write(s7)
#   f.write(s8)
          
# subprocess.call("dummy.bat", shell=True)
# subprocess.call("dummy.bat", shell=True)

# subprocess.call("viewer.bat", shell=True)



