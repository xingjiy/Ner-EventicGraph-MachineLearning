import os
import jieba
LTP_DATA_DIR = r'D:\pycharm\untitled3\NLP\LTP\LtpModel'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`ner.model`
pisrl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl.model')
parser_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')
user_dict_path = os.path.join(LTP_DATA_DIR, r'D:\pycharm\untitled3\NLP\User_dict\user_dict.txt') #词典地址

jieba.load_userdict(user_dict_path)  #导入用户词典

from pyltp import Segmentor  #分词
segmentor = Segmentor()  # 初始化实例
segmentor.load_with_lexicon(cws_model_path, user_dict_path) # 加载模型，第二个参数是您的外部词典文件路径
strte = '实际产能减少、猪肉价格严重分化、跨省运输停滞，北方生猪养殖企业大面积亏损'
#words = segmentor.segment(strte)
seg = jieba.cut(strte, cut_all=False)  #采用jieba精确模式分词
#seg = ' '.join(seg)
words = []
for i in seg:
    words.append(i)

from pyltp import SementicRoleLabeller,Postagger,Parser   #词性标注
postagger = Postagger() # 初始化实例
postagger.load(pos_model_path)  # 加载模型
from pyltp import NamedEntityRecognizer  #命名实体识别
recognizer = NamedEntityRecognizer() # 初始化实例
recognizer.load(ner_model_path)  # 加载模型


#words = segmentor.segment('杨纪星很喜欢一个人玩')  # 分词
print ('\t'.join(words))
postags = postagger.postag(words)  # 词性标注
print('\t'.join(postags))
netags = recognizer.recognize(words, postags)  # 命名实体识别
print('\t'.join(netags))
#print(netags[1]=='O')

# pyltp语义角色标注
def get_roles_by_pyltp(words, postags, arcs):

    roles_list = list()
    # 语义角色标注模型路径，模型名称为‘pisrl.model’

    labeller = SementicRoleLabeller()  # 初始化实例
    labeller.load(pisrl_model_path)
    roles = labeller.label(words, postags, arcs)  # 语义角色标注

    labeller.release()
    # 尝试释放内存
    # import gc
    # del labeller
    # gc.collect()
    # 算了，这个不行
    # roles_list = list(roles)

    return roles



parser=Parser()#初始化实例
parser.load(parser_model_path)
arcs=parser.parse(words,postags)#依存语义分析

'''
labeller=SementicRoleLabeller()#初始化实例
labeller.load(pisrl_model_path)
roles=labeller.label(words,postags,arcs)#语义角色标注
'''
print(arcs)
roles = get_roles_by_pyltp(words,postags,arcs)
print(roles)

for role in roles:
    print(role.index,"".join(["%s:(%d,%d)"%(arg.name,arg.range.start,arg.range.end) for arg in role.arguments]))



