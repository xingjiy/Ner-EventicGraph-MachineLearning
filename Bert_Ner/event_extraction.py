import os
from Bert_Ner.train import *
from NLP_Eventextractor.LTP.PyLTP import PyLtp
from NLP_Eventextractor.jaccard_coefficient import Jaccrad
from IO.event_graph import EventGraph
text_path = r"E:\PyCharm\Python_code\NLP\Ner\Data\text.txt"

class FileOperation:
    # 定义事件关系文件名称
    EVENT_RELATIONS_LIST_FILE_NAME = os.path.join(
        os.path.abspath(os.path.dirname(os.path.realpath(__file__))), "../Data/event_relations_list.csv")
    EVENT_RELATIONS_FILE_NAME = os.path.join(
        os.path.abspath(os.path.dirname(os.path.realpath(__file__))), "../Data/event_relations.csv")
    NEWS_DATA_FILE_NAME = os.path.join(
        os.path.abspath(os.path.dirname(os.path.realpath(__file__))), "../Data/news_data.csv")
    TEST_TEXT_FILE = os.path.join(
        os.path.abspath(os.path.dirname(os.path.realpath(__file__))), "../Data/text.txt")

    def __init__(self):
        pass

    def get_event_relations_list_file(self, event_sets_list):
        fd = open(self.EVENT_RELATIONS_LIST_FILE_NAME, 'a',encoding='utf-8')

        events_list_pre = event_sets_list[0]
        events_list_post = event_sets_list[2]

        if events_list_pre and events_list_post:
            output_line = ''.join(events_list_pre) + ',' + event_sets_list[1] + ',' + ''.join(events_list_post) + '\n'
            fd.write(output_line)
        return

    def event_extraction(self,event_text,start,end):
        fd = open(event_text, 'r', encoding='utf-8')
        file_rows_list = list()
        if start >= end:
            return file_rows_list
        # 防止内存太小而只读一定的文本行
        # file_rows_list = fd.readlines()
        for index in range(0, end):
            if index < start:
                fd.readline()
            else:
                # 去除文中空格与末尾换行（只限中文文本）
                file_rows_list.append(fd.readline().replace(' ', '').rstrip('\n'))
        fd.close()
        return file_rows_list

    def write_event_relations_list(self, event_relations_list):
        num = 0
        Ner = NamedEntityRecognizer(trans=K.eval(CRF.trans), starts=[0], ends=[0])
        with open(self.EVENT_RELATIONS_LIST_FILE_NAME, 'w', encoding='utf-8') as f:
            for event_relation in event_relations_list:
                cause_text = []
                effect_text = []
                predict = Ner.recognize(event_relation)
                for pre_text in predict:
                    if pre_text[1] == 'cause':
                        cause_text.append(pre_text[0])
                    elif pre_text[1] == 'effect':
                        effect_text.append(pre_text[0])
                # print(event_relation)
                # print(predict)
                # print(cause_text)
                #print(effect_text)
                num_pre = len(cause_text)
                num_post = len(effect_text)
                for i in range(num_pre):  # 若因事件有多种、果事件有多种，则根据笛卡尔积进行匹配写入文件
                    for j in range(num_post):
                        event_relation_triples = []
                        event_relation_triples.append(cause_text[i] + ',causality,' + effect_text[j])
                        num = num + 1
                        f.write(event_relation_triples[0] + '\n')
                        #print(event_relation_triples)

    def get_Jaccard_MergeEvent(self, event_relation):  # 基于Jaccard相似度合并节点
        with open(self.EVENT_RELATIONS_FILE_NAME, 'w', encoding='utf-8') as fd:
            pyltp = PyLtp()
            # event_relation为事件组列表
            Nodes = []  # 提取独一的节点
            for event in event_relation:
                if (event[0]) not in Nodes:
                    Nodes.append(event[0])
                if (event[2]) not in Nodes:
                    Nodes.append(event[2])
            print(Nodes)
            flag_pre = 0  # 设置功能标签
            flag_post = 0
            for event_relat in event_relation:  # 依次对事件关系组进行事件合并
                # print()
                #print(event_relat)

                Jaccard_event = []  # 相似节点列表
                for node in Nodes:  # 若因节点相似度与独一节点组中的某个节点相似度超过0.5或节点ATT定中关系一致，则将此node加入相似节点列表
                    if Jaccrad(event_relat[0], node) >= 0.5 and pyltp.get_ATT(event_relat[0]) == pyltp.get_ATT(node):
                        Jaccard_event.append(node)
                        #print(event_relat[0], '=', node)
                        # event_relat[0] = node
                        flag_pre = 1
                if flag_pre == 1:  # 若存在这样的相似节点，则将相似节点列表第一个节点进行替换
                    # print(Jaccard_event)
                    #print(event_relat[0], '=', Jaccard_event[0])
                    event_relat[0] = Jaccard_event[0]

                Jaccard_event = []  # 重置相似节点列表
                for node in node:  # 果节点处理
                    if Jaccrad(event_relat[2], node) >= 0.5 and pyltp.get_ATT(event_relat[2]) == pyltp.get_ATT(node):
                        Jaccard_event.append(node)
                        # print(event_relat[2], '=', node)
                        # event_relat[2] = node
                        flag_post = 1
                if flag_post == 1:
                    # print(Jaccard_event)
                    # print(event_relat[2], '=', Jaccard_event[0])
                    event_relat[2] = Jaccard_event[0]
                #print(event_relat)

                events_list_pre = event_relat[0]
                events_list_post = event_relat[2]
                if events_list_pre and events_list_post:
                    output_line = ''.join(events_list_pre) + ',' + event_relat[1] + ',' + ''.join(
                        events_list_post) + '\n'
                    print(output_line)
                    fd.write(output_line)  # 将合并替换后的节点重新导入进event_relations.csv文件中
            # 将相似度较高节点的进行归并


if __name__ == '__main__':
    file_operation = FileOperation()
    event_text = file_operation.event_extraction(text_path, 0, 1400) # 事件
    file_operation.write_event_relations_list(event_text)  # 事件关系抽取
    event_graph = EventGraph()
    nodes_and_edges = event_graph.get_graph_nodes_and_edges()   # 事件图
    print(nodes_and_edges)
    file_operation.get_Jaccard_MergeEvent(nodes_and_edges[1])  # 根据相似度合并节点
    print("Nodes:")
    print(nodes_and_edges[0])
    print("Edges:")
    for i in nodes_and_edges[1]:
        print(i)
