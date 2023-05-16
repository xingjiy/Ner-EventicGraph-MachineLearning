#! -*- coding: utf-8 -*-
import os
import sys
import random
import pickle
import numpy as np
from tqdm import tqdm
import tensorflow as tf
from bert4keras.backend import K,keras,search_layer
from bert4keras.snippets import ViterbiDecoder, to_array

from data_utils import *
from build_model import bert_bilstm_crf

seed = 233
#tf.random.set_seed(seed)
#tf.random.set_seed()
tf.random.set_random_seed(seed)
np.random.seed(seed)
random.seed(seed)
os.environ['PYTHONHASHSEED'] = str(seed)

epochs = 12
max_len = 70
batch_size = 16
lstm_units = 128
drop_rate = 0.1
leraning_rate = 1e-5

config_path = r'E:\PyCharm\Python_code\NLP\Ner\Bert_Ner\chinese_L-12_H-768_A-12/bert_config.json'
checkpoint_path = r'E:\PyCharm\Python_code\NLP\Ner\Bert_Ner\chinese_L-12_H-768_A-12/bert_model.ckpt'
checkpoint_save_path = './checkpoint/bert_bilstm_crf.weights'

class NamedEntityRecognizer(ViterbiDecoder):
    """命名实体识别器
    """
    def recognize(self, text):
        tokens = tokenizer.tokenize(text)
        while len(tokens) > max_len:
            tokens.pop(-2)
        mapping = tokenizer.rematch(text, tokens)  # 还原映射
        token_ids = tokenizer.tokens_to_ids(tokens)  # 转换为ids
        segment_ids = [0] * len(token_ids)
        token_ids, segment_ids = to_array([token_ids], [segment_ids]) # ndarray
        nodes = model.predict([token_ids, segment_ids])[0] # [sqe_len,23]
        labels = self.decode(nodes) # id [sqe_len,], [0 0 0 0 0 7 8 8 0 0 0 0 0 0 0]
        entities, starting = [], False
        for i, label in enumerate(labels):
            if label > 0:
                if label % 2 == 1:
                    starting = True
                    entities.append([[i], id2label[(label - 1) // 2]])
                elif starting:
                    entities[-1][0].append(i)
                else:
                    starting = False
            else:
                starting = False
        return [(text[mapping[w[0]][0]:mapping[w[-1]][-1] + 1], l) for w, l in entities]

def ner_metricts(data):  #命名实体识别评估指标
    X,Y,Z, = 1e-6,1e-6,1e-6
    for d in tqdm(data):
        text = ''.join([i[0] for i in d])
        pred = NER.recognize(text)
        R = set(pred)  # 预测的实体
        T = set([tuple(i) for i in d if i[1] != 'O']) # 标注的实体
        X += len(R & T)
        Y += len(R)
        Z += len(T)
    f1,precision,recall = 2*X/(Y+Z),X/Y,X/Z # F1,准确率,召回率
    return f1,precision,recall

class Evaluator(keras.callbacks.Callback):  #训练过程中的评估
    def __init__(self):
        super(Evaluator).__init__()
        self.best_val_f1 = 0
    def on_epoch_end(self, epoch,logs=None):  #每一个epoch结束时调用
        NER.trans = K.eval(CRF.trans) #更新概率转移矩阵
        f1,precision,recall = ner_metricts(valid_data)
        if f1 > self.best_val_f1:
            model.save_weights(checkpoint_save_path)
            self.best_val_f1 = f1
            print('save model to {}'.format(checkpoint_save_path))
        else:
            global leraning_rate
            leraning_rate /= 5
        print('valid: f1: %.4f, precision: %.4f, recall: %.4f, best_f1: %.1e' % (f1,precision,recall,self.best_val_f1))


model,CRF = bert_bilstm_crf(
        config_path,checkpoint_path,num_labels,lstm_units,drop_rate,leraning_rate)
NER = NamedEntityRecognizer(trans=K.eval(CRF.trans), starts=[0], ends=[0])

if __name__ == '__main__':

    train_data,_ = load_data(r'E:\PyCharm\Python_code\NLP\Ner\Bert_Ner\data/train.char',max_len)
    valid_data,_ = load_data(r'E:\PyCharm\Python_code\NLP\Ner\Bert_Ner\data/dev.char',max_len)

    train_generator = data_generator(train_data, batch_size)
    valid_generator = data_generator(valid_data, batch_size*5)

    checkpoint = keras.callbacks.ModelCheckpoint(
        checkpoint_save_path, 
        monitor='val_sparse_accuracy', 
        verbose=1, 
        save_best_only=True,
        mode='max'
        )
    Evaluator = Evaluator()
    model.fit(
        train_generator.forfit(),
        steps_per_epoch=len(train_generator),
        validation_data=valid_generator.forfit(),
        validation_steps=len(valid_generator),
        epochs=epochs,
        callbacks=[Evaluator]
    )

    print(K.eval(CRF.trans))
    print(K.eval(CRF.trans).shape)
    pickle.dump(K.eval(CRF.trans),open('./checkpoint/crf_trans.pkl','wb'))

else:
    model.load_weights(checkpoint_save_path)
    NER.trans = pickle.load(open('./checkpoint/crf_trans.pkl','rb'))