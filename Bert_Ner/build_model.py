import keras
from bert4keras.models import build_transformer_model
from bert4keras.optimizers import Adam
from bert4keras.tokenizers import Tokenizer
from bert4keras.layers import ConditionalRandomField
import keras.backend as K
class SetLearningRate:
    """层的一个包装，用来设置当前层的学习率
    """
    def __init__(self, layer, lamb, is_ada=False):
        self.layer = layer
        self.lamb = lamb # 学习率比例
        self.is_ada = is_ada # 是否自适应学习率优化器

    def __call__(self, inputs):
        with K.name_scope(self.layer.name):
            if not self.layer.built:
                input_shape = K.int_shape(inputs)
                self.layer.build(input_shape)
                self.layer.built = True
                if self.layer._initial_weights is not None:
                    self.layer.set_weights(self.layer._initial_weights)
        for key in ['kernel', 'bias', 'embeddings', 'depthwise_kernel', 'pointwise_kernel', 'recurrent_kernel', 'gamma', 'beta']:
            if hasattr(self.layer, key):
                weight = getattr(self.layer, key)
                if self.is_ada:
                    lamb = self.lamb # 自适应学习率优化器直接保持lamb比例
                else:
                    lamb = self.lamb**0.5 # SGD（包括动量加速），lamb要开平方
                K.set_value(weight, K.eval(weight) / lamb) # 更改初始化
                setattr(self.layer, key, weight * lamb) # 按比例替换
        return self.layer(inputs)


def bert_bilstm_crf(config_path,checkpoint_path,num_labels,lstm_units,drop_rate,learning_rate):
    bert = build_transformer_model(
        config_path = config_path, # 配置文件路径
        checkpoint_path = checkpoint_path, # 模型权重路径
        model='bert',  # 模型类型，可选值为bert, lstm, bilstm, cnn, rcnn, crf
        return_keras_model = False, # 返回keras模型
        )
    x = bert.model.output # 输出层 [batch_size, sequence_length, embedding_size:768]
    lstm = SetLearningRate(
            keras.layers.Bidirectional(
                keras.layers.LSTM(
                    lstm_units,  # 隐藏层神经元数量
                    kernel_initializer='he_normal',  # 权重初始化方式
                    return_sequences=True,  # 是否返回序列值
                )
            ),
            100,
            True
            )(x)    # 双向LSTM层 [batch_size, sequence_length, lstm_units*2]
    x = keras.layers.concatenate(
        [lstm, x],
        axis=-1,
    ) # 合并层 [batch_size, sequence_length, lstm_units*2+embedding_size:768]
    x = keras.layers.TimeDistributed(
            keras.layers.Dropout(drop_rate)
            )(x)  # TimeDistributed层 [batch_size, sequence_length, lstm_units*2]
    x = SetLearningRate(
        keras.layers.TimeDistributed(
            keras.layers.Dense(
                num_labels,
                activation='relu',
                kernel_initializer='he_normal'
                )
             ),
            100,
            True
        )(x) # TimeDistributed层 [batch_size, sequence_length, num_labels]

    crf = ConditionalRandomField()
    output = crf(x) # CRF层 [batch_size, sequence_length, num_tags]

    model = keras.models.Model(bert.input, output)
    model.compile(
        loss=crf.sparse_loss, # 交叉熵作为损失函数
        optimizer=Adam(learning_rate), # 优化器 # 参数设置
        metrics=[crf.sparse_accuracy], # 评估指标 #
    )

    return model,crf

if __name__ == '__main__':
    config_path = r'E:\PyCharm\Python_code\NLP\Ner\bert_for_ner\chinese_L-12_H-768_A-12/bert_config.json'
    checkpoint_path = r'E:\PyCharm\Python_code\NLP\Ner\bert_for_ner\chinese_L-12_H-768_A-12/bert_model.ckpt'
    num_labels = 21
    lstm_units = 128
    drop_rate = 0.1
    learning_rate = 5e-5
    model,crf = bert_bilstm_crf(config_path,checkpoint_path,num_labels,lstm_units,drop_rate,learning_rate)
    print(model.summary())