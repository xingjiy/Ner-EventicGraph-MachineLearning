#! -*- coding: utf-8 -*-

import numpy as np
from tqdm import tqdm
from metrics import *
from train import *
from data_utils import load_data

def predict_label(data):
    y_pred = []
    for d in tqdm(data):
        text = ''.join([i[0] for i in d])
        pred = NER.recognize(text)
        
        label = ['O' for _ in range(len(text))]
        b = 0
        for item in pred:
            word,typ = item[0],item[1]
            start = text.find(word,b)
            end = start + len(word)
            label[start] = 'B-' + typ
            for i in range(start + 1, end):
                label[i] = 'I-' + typ
            b += len(word)

        y_pred.append(label)

    return y_pred

def evaluate():
    data_path = r'E:\Python_test\Bert_Ner\data/dev.char'
    test_data, y_true = load_data(data_path,70)
    y_pred = predict_label(test_data)

    f1 = f1_score(y_true,y_pred,suffix=False)
    p = precision_score(y_true,y_pred,suffix=False)
    r = recall_score(y_true,y_pred,suffix=False)
    acc = accuracy_score(y_true,y_pred)

    print("f1_score: {:.4f}, precision_score: {:.4f}, recall_score: {:.4f}, accuracy_score: {:.4f}".format(f1,p,r,acc))
    print(classification_report(y_true, y_pred, digits=4, suffix=False))

#def event_extraction(event_text):


if __name__ == '__main__':
    #evaluate()
    Ner = NamedEntityRecognizer(trans=K.eval(CRF.trans), starts=[0], ends=[0])
    text1 = ['今年第一季度工厂用工成本提升以及上游原绒价格上涨，导致年底羊绒及服装业务毛利率下滑','非洲猪瘟持续使得市场猪肉价格上涨，北方生猪养殖企业亏损以及饲料价格下跌','巴西矿难及飓风对发运的影响，导致铁矿石供应下降',"今年三月份非洲猪瘟持续影响使得市场猪肉存量下降和猪肉价格上升"]
    text = '今年第一季度工厂用工成本提升以及上游原绒价格上涨，导致年底羊绒及服装业务毛利率下滑'
    for t in text1:
        pred = Ner.recognize(t)
        # print(pred)
        print(t)
        for i in pred:
            print(i)
    #pred = Ner.recognize('非洲猪瘟持续使得市场猪肉价格上涨，北方生猪养殖企业亏损以及饲料价格下跌')
    #pred = Ner.recognize('巴西矿难及飓风对发运的影响，导致铁矿石供应下降')
    # pred = Ner.recognize(text)
    #print(pred)
    # print(text)
    # for i in pred:
    #     print(i)
