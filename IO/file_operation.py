import os
import numpy as np
from scrapy.exporters import CsvItemExporter
from NLP_Eventextractor import  event_relation_extractor,event_extractor
from NLP_Eventextractor.LTP.PyLTP import PyLtp
from IO import event_graph
from NLP_Eventextractor.jaccard_coefficient import Jaccrad
text_path = r"E:\PyCharm\Python_code\NLP\Ner\Data\text.txt"
ccks_task2_train = r"E:\PyCharm\Python_code\NLP\Ner\Data\ccks_task2_train.csv"
ccks_task2_eval_data = r"E:\PyCharm\Python_code\NLP\Ner\Data\ccks_task2_eval_data.csv"

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

    # 从文件中得到一定数量的一行一行的文本
    def get_file_rows_list(self, filename, start, end):
        fd = open(filename, 'r',encoding='utf-8')
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

    # 将输出的事件关系对转化为csv文本
    def get_event_relations_list_file(self, event_sets_list):
        fd = open(self.EVENT_RELATIONS_LIST_FILE_NAME, 'a',encoding='utf-8')

        events_list_pre = event_sets_list[0]
        events_list_post = event_sets_list[2]

        if events_list_pre and events_list_post:
            output_line = ''.join(events_list_pre) + ',' + event_sets_list[1] + ',' + ''.join(events_list_post) + '\n'
            fd.write(output_line)
        return

    # 输出新闻csv文件
    def get_news_list_file(self, item):
        file = open(self.NEWS_DATA_FILE_NAME, 'ab')
        exporter = CsvItemExporter(file, encoding='UTF-8')
        exporter.start_exporting()
        exporter.export_item(item)
        exporter.finish_exporting()
        file.close()

    def get_event_SBV(self,text_list): #得到初始事件三元组,将事件ATT+SBV形式写入事件三元组
        event_relation_extract = event_relation_extractor.EventRelationExtractor()
        num = 0
        n = 0
        for t_list in text_list:
            if len(t_list) == 0:  #若事件为空，则跳过
                continue
            event_relation_triples = event_relation_extract.event_relation_extrator_main(t_list)  #将事件分为因事件、触发词、果事件三元组
            # print(event_relation_triples)
            event_relation_triples = list(np.ravel(event_relation_triples)) #得到初始事件三元组
            print(event_relation_triples)
            pyltp = PyLtp()
            #print(len(event_relation_triples))
            if len(event_relation_triples) == 0:  #若事件关系为空，则跳过
                continue
            event_pre = pyltp.Parser(event_relation_triples[0])  # 利用pyltp提出事件ATT+SBV
            event_post = pyltp.Parser(event_relation_triples[2])
            if len(event_pre) == 0 :
                continue
            print(event_pre)
            print(event_post)
            num_pre = len(event_pre)
            num_post = len(event_post)
            #n = n+1
            #print(n)
            for i in range(num_pre):  #若因事件有多种、果事件有多种，则根据笛卡尔积进行匹配写入文件
                for j in range(num_post):
                    event_relation_triples[0] = event_pre[i]
                    event_relation_triples[2] = event_post[j]
                    num = num + 1
                    #print(num)
                    file_operation.get_event_relations_list_file(event_relation_triples) #将事件SBV形式写入事件三元组

        return


    def get_Jaccard_MergeEvent(self,event_relation):  #基于Jaccard相似度合并节点
        pyltp = PyLtp()
        #event_relation为事件组列表
        Nodes = []  #提取独一的节点
        for event in event_relation:
            if (event[0]) not in Nodes:
                Nodes.append(event[0])
            if (event[2]) not in Nodes:
                Nodes.append(event[2])
        #print(Nodes)
        flag_pre = 0   #设置功能标签
        flag_post = 0
        for event_relat in event_relation:  #依次对事件关系组进行事件合并
            #print()
            #print(event_relat)

            Jaccard_event = []   #相似节点列表
            for node in Nodes:    #若因节点相似度与独一节点组中的某个节点相似度超过0.5或节点ATT定中关系一致，则将此node加入相似节点列表
                if Jaccrad(event_relat[0],node)>=0.5 and pyltp.get_ATT(event_relat[0]) == pyltp.get_ATT(node):
                    Jaccard_event.append(node)
                    #print(event_relat[0], '=', node)
                    #event_relat[0] = node
                    flag_pre = 1
            if flag_pre == 1:  #若存在这样的相似节点，则将相似节点列表第一个节点进行替换
                #print(Jaccard_event)
                #print(event_relat[0], '=', Jaccard_event[0])
                event_relat[0] = Jaccard_event[0]

            Jaccard_event = []  #重置相似节点列表
            for node in node:   #果节点处理
                if Jaccrad(event_relat[2],node)>=0.5 and pyltp.get_ATT(event_relat[2]) == pyltp.get_ATT(node):
                    Jaccard_event.append(node)
                    #print(event_relat[2], '=', node)
                    #event_relat[2] = node
                    flag_post = 1
            if flag_post == 1:
                #print(Jaccard_event)
                #print(event_relat[2], '=', Jaccard_event[0])
                event_relat[2] = Jaccard_event[0]

            fd = open(self.EVENT_RELATIONS_FILE_NAME, 'a', encoding='utf-8')
            events_list_pre = event_relat[0]
            events_list_post = event_relat[2]
            if events_list_pre and events_list_post:
                output_line = ''.join(events_list_pre) + ',' + event_relat[1] + ',' + ''.join(
                    events_list_post) + '\n'
                fd.write(output_line)     #将合并替换后的节点重新导入进event_relations.csv文件中
        #将相似度较高节点的进行归并



if __name__ == '__main__':
    file_operation = FileOperation()
    text_list = file_operation.get_file_rows_list(text_path,0,1400) #提取前n个事件
    #得到初始事件三元组,将事件SBV形式写入事件三元组
    file_operation.get_event_SBV(text_list)
    event_graph =event_graph.EventGraph()
    nodes_and_edges = event_graph.get_graph_nodes_and_edges() #得到节点和关系线
    print(len(nodes_and_edges[1]))
    print(nodes_and_edges)
    file_operation.get_Jaccard_MergeEvent(nodes_and_edges[1]) #根据相似度合并节点
    print("Nodes:")
    print(nodes_and_edges[0])
    print("Edges:")
    for i in nodes_and_edges[1]:
        print(i)

