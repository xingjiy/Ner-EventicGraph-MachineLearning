# import numpy as np
# from scipy.spatial.distance import pdist#直接调包可以计算JC值 :需要两个句子长度一样；所以暂时不用
import jieba


def Jaccrad(model, reference):  # terms_reference为源句子，terms_model为候选句子
    terms_reference = jieba.cut(reference)  # 默认精准模式
    terms_model = jieba.cut(model)
    grams_reference = set(terms_reference)  # 去重；如果不需要就改为list
    grams_model = set(terms_model)
    temp = 0
    for i in grams_reference:
        if i in grams_model:
            temp = temp + 1
    fenmu = len(grams_model) + len(grams_reference) - temp  # 并集
    jaccard_coefficient = float(temp / fenmu)  # 交集
    return jaccard_coefficient


if __name__ == '__main__':
    a = "鸡苗价格下跌"
    b = "白糖价格下跌"
    c = '非洲猪瘟爆发'
    d = '产能减少'
    e = '生猪价格维持'
    jaccard_coefficient = Jaccrad(a, b)
    print(jaccard_coefficient)