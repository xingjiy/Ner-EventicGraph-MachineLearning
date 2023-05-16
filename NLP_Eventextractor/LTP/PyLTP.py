import os
import jieba
from pyltp import Segmentor  # 分词
from pyltp import SementicRoleLabeller, Postagger, Parser  # 词性标注
from pyltp import NamedEntityRecognizer  # 命名实体识别
LTP_DATA_DIR = r'E:\PyCharm\Python_code\NLP\Ner\NLP_Eventextractor\LTP\LtpModel'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`ner.model`
pisrl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl.model')
parser_model_path = os.path.join(LTP_DATA_DIR, 'parser.model') # 依存句法分析模型，模型名称为`parser.model`
user_dict_path = os.path.join(LTP_DATA_DIR, r'E:\PyCharm\Python_code\NLP\Ner\User_dict\user_dict.txt') #词典地址

jieba.load_userdict(user_dict_path)  #导入用户词典
segmentor = Segmentor()  # 初始化实例
# segmentor.load()  # 加载模型
segmentor.load_with_lexicon(cws_model_path, user_dict_path)  # 加载模型，第二个参数是您的外部词典文件路径
postagger = Postagger()  # 初始化实例
postagger.load(pos_model_path)  # 加载模型
parser = Parser()  # 初始化实例
parser.load(parser_model_path)
recognizer = NamedEntityRecognizer()  # 初始化实例
recognizer.load(ner_model_path)  # 加载模型
class PyLtp:
    def Segmentor(self,centents):
        # 分词
        #strte = '巴西矿难及飓风对发运的影响，导致铁矿石全年供应走低'
        # words = segmentor.segment(strte)
        seg = jieba.cut(centents, cut_all=False)  # 采用jieba精确模式分词
        # seg = ' '.join(seg)
        words = []
        for i in seg:
            words.append(i)
        return words


    def Postagger(self,centents):
        # 词性标注
        words = self.Segmentor(centents)
        postags = postagger.postag(words)  # 词性标注
        #print('\t'.join(words))
        #print('\t'.join(postags))
        return postags


    def get_ATT(self,centents):
        ATT_node1 = ''
        word_node = self.Segmentor(centents)
        postag_node = self.Postagger(centents)
        arcs_node = parser.parse(word_node, postag_node)  # 依存语义分析
        relation = [arc.relation for arc in arcs_node]  # 提取依存关系
        for i in range(len(word_node)):
            if relation[i] == "ATT":
                ATT_node1 = str(word_node[i])
        return  ATT_node1


# pyltp语义角色标注
    def get_roles_by_pyltp(self,centents):

        roles_list = list()
        # 语义角色标注模型路径，模型名称为‘pisrl.model’
        words = self.Segmentor(centents)
        postags = self.Postagger(centents)

        arcs = parser.parse(words, postags)  # 依存语义分析
        labeller = SementicRoleLabeller()  # 初始化实例
        labeller.load(pisrl_model_path)
        roles = labeller.label(words, postags, arcs)  # 语义角色标注

        labeller.release()
        return roles


    def Parser(self,centents):
        words = self.Segmentor(centents)
        postags = self.Postagger(centents)
        arcs = parser.parse(words, postags)  # 依存语义分析
        rely_id = [arc.head for arc in arcs]  # 提取依存父节点id
        relation = [arc.relation for arc in arcs]  # 提取依存关系
        heads = ["Root" if id == 0 else words[id - 1] for id in rely_id]  # 匹配依存父节点词语
        ATT = []
        SBV = []
        #print(words)
        global Att
        Att = ''
        for i in range(len(words)):
            if relation[i] == "ATT":
                ATT.append(words[i]+heads[i])
                Att = str(words[i])
                #print(Att)
                #print(relation[i] + "(" + words[i] + ", " + heads[i] + ")")

            if relation[i] == "SBV":
                #print(words[i]+heads[i])
                SBV.append(Att+words[i]+heads[i])
                #print(relation[i] + "(" + words[i] + ", " + heads[i] + ")")
                #print(Att+words[i]+heads[i])

        return SBV

        '''
        roles = self.get_roles_by_pyltp(centents)
        for role in roles:
            print(role.index,"".join(["%s:(%d,%d)"%(arg.name,arg.range.start,arg.range.end) for arg in role.arguments]))

        '''



if __name__ == "__main__":
    pyltp = PyLtp()
    centents = "实际产能减少、猪肉价格严重分化、跨省运输停滞，北方生猪养殖企业大面积亏损"
    centents1 = "国内汽柴油价格下调，导致炼油损耗逐月扩大、库存价格下跌"
    print(pyltp.Segmentor(centents1))
    print(pyltp.Postagger(centents1))
    #print(pyltp.get_roles_by_pyltp(centents))
    print(pyltp.Parser(centents1))




