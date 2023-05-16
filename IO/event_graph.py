import os
from IO.database_operation import MongoOperation


class EventGraph:
    # 关系文件位置
    EVENT_RELATIONS_LIST_FILE_NAME = os.path.join(
        os.path.abspath(os.path.dirname(os.getcwd())), "Data/event_relations_list.csv")

    def __init__(self):
        fd = open(self.EVENT_RELATIONS_LIST_FILE_NAME, 'r' , encoding='utf-8')
        self.event_triple_sets = fd.readlines()
        #print('\n'.join(self.event_triple_sets))
        #self.event_triple_sets = db.event_db_get()
        #print('\n'.join(self.event_triple_sets))

    # 统计事件频次
    def get_frequence(self):
        event_dict = dict()
        relation_dict = dict()
        node_dict = dict()
        for event_triple_set in self.event_triple_sets:
            event_triple = event_triple_set.strip()
            if not event_triple:
                continue
            nodes = event_triple.split(',')
            relation = nodes.pop(1)
            for node in nodes:
                if node not in node_dict:
                    node_dict[node] = 1
                else:
                    node_dict[node] += 1
            if relation not in relation_dict:
                relation_dict[relation] = 1
            else:
                relation_dict[relation] += 1
            if event_triple not in event_dict:
                event_dict[event_triple] = 1
            else:
                event_dict[event_triple] += 1
        return [node_dict, relation_dict, event_dict]

    # 构建事理图谱的节点和边
    def get_graph_nodes_and_edges(self):
        edges = list()
        nodes = list()
        frequence_static = self.get_frequence()
        node_dict = frequence_static[0]
        relation_dict = frequence_static[1]
        event_dict = frequence_static[2]
        # 将event_dict降序排列取前500位
        for event_triple_set in sorted(event_dict.items(), key=lambda asd: asd[1], reverse=True)[:2000]:
            event_triple = event_triple_set[0].strip()
            e1 = event_triple.split(',')[0]
            r = event_triple.split(',')[1]
            e2 = event_triple.split(',')[2]
            if e1 in node_dict and e2 in node_dict and r in relation_dict:
                nodes.append(e1)
                nodes.append(e2)
                edges.append([e1, r, e2])
            else:
                continue
        return [nodes, edges]


if __name__ == "__main__":
    event_graph = EventGraph()
    nodes_and_edges = event_graph.get_graph_nodes_and_edges()
    print(nodes_and_edges)
    print("Nodes:")
    print(nodes_and_edges[0])
    print("Edges:")
    print(nodes_and_edges[1])
