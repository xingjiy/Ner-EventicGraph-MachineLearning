# @Author:YangJixing
# -*- codeing = utf-8 -*-
# @Time :2022-4-13 14:52
# @File :json_get.py
# @Software : PyCharm


import json
path1 = r"D:\pycharm\untitled3\NLP\Data\ccks_task2_train.txt"
path2 = r"D:\pycharm\untitled3\NLP\Data\ccks_task2_eval_data.txt"
ccks_task2_train = r"D:\pycharm\untitled3\NLP\Data\ccks_task2_train.csv"
ccks_task2_eval_data = r"D:\pycharm\untitled3\NLP\Data\ccks_task2_eval_data.csv"
fd = open(ccks_task2_train, 'a',encoding='utf-8')

with open(path1, 'r', encoding='utf-8') as f:
    for jsonstr in f.readlines():
        data = json.loads(jsonstr)
        text = data['text']
        print(text)
        output_line = ''.join(text) + '\n'
        fd.write(output_line)
