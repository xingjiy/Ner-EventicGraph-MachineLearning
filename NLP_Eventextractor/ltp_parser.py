import os
import re
from pyltp import SentenceSplitter, Segmentor, Postagger, NamedEntityRecognizer, Parser, SementicRoleLabeller
LTP_DATA_DIR = r'D:\pycharm\untitled3\NLP\LTP\LtpModel'  # ltp模型目录的路径
pisrl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl.model')
parser_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')

class LtpParser:
    def __init__(self):
        self.ltp_dir_path = r'D:\pycharm\untitled3\NLP\LTP\LtpModel'
        pass

    # 长句切分。将段落分句，将一段话或一篇文章中的文字按句子分开，按句子形成独立的单元。返回切分好的句子列表
    def get_sentences(self, content):
        # 消去句子中的空格以及换行
        content = content.replace(' ', '').replace('\n', '',)
        sents = SentenceSplitter.split(content)
        sents_list = list(sents)
        return sents_list

    # 短句切分。将长句按逗号和顿号切分为短句。返回切分好的短句列表
    def get_subsents(self, sentence):
        subsents_list = list()
        # 将括号里的语句也分割出来
        subsents = re.split(r'[，,：:]', sentence)
        # 消去长度为0的子句，并将子句加入列表中
        for subsent in subsents:
            if subsent:
                subsents_list.append(subsent)
        return subsents_list

    # pyltp分词
    def get_words_by_pyltp(self, sent):
        words_list = list()
        # 分词模型路径，模型名称为’cws.model‘
        cws_model_path = os.path.join(self.ltp_dir_path, "cws.model")
        # dict是自定义词典的文件路径
        dict_path = os.path.join(self.ltp_dir_path, "dict.txt")
        segmentor = Segmentor()
        segmentor.load_with_lexicon(cws_model_path, dict_path)
        words = segmentor.segment(sent)
        segmentor.release()
        words_list = list(words)
        return words_list

    # pyltp标注词性
    def get_postags_by_pyltp(self, words_list):
        postags_list = list()
        # 词性标注模型路径，模型名称为‘pos.model’
        pos_model_path = os.path.join(self.ltp_dir_path, "pos.model")
        postagger = Postagger()
        postagger.load(pos_model_path)
        postags = postagger.postag(words_list)
        postagger.release()
        postags_list = list(postags)
        return postags_list

    # pyltp命名实体识别
    def get_netags_by_pyltp(self, words_list, postags_list):
        netags_list = list()
        # 实体命名识别模型路径，模型名称为‘ner.model’
        ner_model_path = os.path.join(self.ltp_dir_path, "ner.model")
        recognizer = NamedEntityRecognizer()
        recognizer.load(ner_model_path)
        netags = recognizer.recognize(words_list, postags_list)
        recognizer.release()
        netags_list = list(netags)
        return netags_list

    # pyltp依存句法分析
    def get_arcs_by_pyltp(self, words_list, postags_list):
        arcs_list = list()
        # 依存句法分析模型路径，模型名称为‘parser.model’
        par_model_path = os.path.join(self.ltp_dir_path, "parser.model")
        parser = Parser()
        parser.load(par_model_path)
        arcs = parser.parse(words_list, postags_list)
        parser.release()
        return arcs

    # pyltp语义角色标注
    def get_roles_by_pyltp(self,words_list, postags_list, arcs):
        roles_list = list()
        # 语义角色标注模型路径，模型名称为‘pisrl.model’

        labeller = SementicRoleLabeller()
        labeller.load(pisrl_model_path)
        roles = labeller.label(words_list, postags_list, arcs)


        labeller.release()
        return roles

    # 句法分析，生成词语依存子节点字典列表
    def get_words_child_nodes_dict_list(self, words_list, arcs_list):
        words_child_nodes_dict_list = list()
        for word_index in range(len(words_list)):
            words_child_nodes_dict = dict()
            for arc_index in range(len(arcs_list)):
                # arc_index从1开始，0为root
                if arcs_list[arc_index].head == word_index + 1:
                    # 用词语依存子节点字典来存贮该词依存关系词在分句中的位置
                    # words_list： 1.元芳 2.你 3.怎么 4.看
                    # arcs_list： 4:SBV 4:SBV 4:ADV 0:HED
                    # 则“看”就有3个依存关系，存入词语依存子节点字典中为{SBV:[1,2],ADV:[3]}
                    if arcs_list[arc_index].relation not in words_child_nodes_dict:
                        words_child_nodes_dict[arcs_list[arc_index].relation] = list()
                    words_child_nodes_dict[arcs_list[arc_index].relation].append(arc_index)
            words_child_nodes_dict_list.append(words_child_nodes_dict)
        return words_child_nodes_dict_list

    # 生成语义角色标注字典
    def get_format_roles_dict(self, words_list, postags_list, arcs_list):
        roles_dict = dict()
        roles = self.get_roles_by_pyltp(words_list, postags_list, arcs_list)
        for role in roles:
            roles_dict[role.index] = {arg.name: [arg.name, arg.range.start, arg.range.end] for arg in role.arguments}
        return roles_dict

    # 生成句法分析关系
    def get_format_arcs_list(self, words_list, postags_list, arcs_list):
        format_arcs_list = list()
        # 提取父节点，父节点词语，和依存关系
        arcs_heads = [arc.head for arc in arcs_list]
        arcs_relations = [arc.relation for arc in arcs_list]
        # 如果依存关系的index为0，起名为root，否则在words_list中找到词语
        arcs_head_words = ['root' if index == 0 else words_list[index - 1] for index in arcs_heads]
        for index in range(len(words_list)):
            # 组成格式为['依存关系','子节点词','子节点词句中位置','子节点词性','父节点词','父节点词句中位置','父节点词性']
            format_arc = [arcs_relations[index], words_list[index], index, postags_list[index], \
                          arcs_head_words[index], arcs_heads[index] - 1, postags_list[arcs_heads[index] - 1]]
            format_arcs_list.append(format_arc)
        return format_arcs_list

    # ltp_parser主函数
    def ltp_parser_main(self, content):
        sentences_list = list(self.get_sentences(content))
        subsents_list = list()
        for sentence in sentences_list:
            subsents_list += list(self.get_subsents(sentence))
        datas_list = list()
        for subsent in subsents_list:
            data = dict()
            data['words_list'] = self.get_words_by_pyltp(subsent)
            data['postags_list'] = self.get_postags_by_pyltp(data['words_list'])
            data['arcs_list'] = self.get_arcs_by_pyltp(data['words_list'], data['postags_list'])
            data['roles_dict'] = self.get_format_roles_dict(data['words_list'], data['postags_list'], data['arcs_list'])
            data['child_nodes_dict_list'] = self.get_words_child_nodes_dict_list(data['words_list'], data['arcs_list'])
            data['format_arcs_list'] = self.get_format_arcs_list(\
                data['words_list'], data['postags_list'], data['arcs_list'])
            datas_list.append(data)
        return datas_list


if __name__ == '__main__':
    ltp_parse = LtpParser()
    content = "农业科技创新是一整个流程"
    content1 = '''
        公安部近日组织全国公安机关开展扫黑除恶
        追逃“清零”行动。公安部将1712名涉黑涉恶
        逃犯列为“清零”行动目标逃犯，逐一明确追
        逃责任人，实行挂账督捕，并对13名重点在
        逃人员发布A级通缉令。
        '''
    words_list = ltp_parse.get_words_by_pyltp(content1)
    postags_list = ltp_parse.get_postags_by_pyltp(words_list)
    netags_list = ltp_parse.get_netags_by_pyltp(words_list,postags_list)
    #print(netags_list)
    arcs = ltp_parse.get_arcs_by_pyltp(words_list,postags_list)
    roles_list = ltp_parse.get_roles_by_pyltp(words_list,postags_list,arcs)
    '''
    labeller = SementicRoleLabeller()
    labeller.load(pisrl_model_path)
    roles_list = labeller.label(words_list, postags_list, arcs)
    '''
    #print(roles_list)
    '''
    for role in roles_list:
        print(role.index,"".join(["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))
    '''
    data_list = ltp_parse.ltp_parser_main(content)
    #print(data_list)
    #data_list = "".join(data_list)
    for data in data_list:
        print(data)
    sentences = ltp_parse.get_sentences(content1)
    print(sentences)
