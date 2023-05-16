from py2neo import Graph, Node, Relationship, NodeMatcher, Subgraph, RelationshipMatcher

class Neo4jGraph():


    def Node_Relation(self,event_relation):
        g = Graph('http://localhost:7474', username='neo4j', password='test')
        g.delete_all()    #每次录入节点前清空图谱
        num = len(event_relation)
        Nodes = []
        s = 0

        # 创建节点，节点不重复
        for i in range(num) :
            if event_relation[i][0] not in Nodes:
                #print(event_relation[i][0])
                Nodes.append(event_relation[i][0])
                #print(event_relation[i][0])
                a = Node("event", name=Nodes[s])
                s = s + 1
                #print(i,a)
                g.create(a)

            if event_relation[i][2] not in Nodes:
                #print(event_relation[i][0])
                Nodes.append(event_relation[i][2])
                #print(event_relation[i][2])
                b = Node("event", name=Nodes[s])
                s = s + 1
                #print(i,b)
                g.create(b)

        #为已有节点创建关系边
        #print(num)
        for i in range(num):
            matcher = NodeMatcher(g)
            c = "'{}'".format(event_relation[i][0])
            #print(c)
            Pre = matcher.match('event').where("_.name="+"'{}'".format(event_relation[i][0])).first()   #根据关系中的因节点匹配图中已创建的节点
            Post = matcher.match('event').where("_.name="+"'{}'".format(event_relation[i][2])).first()  #根据关系中的果节点匹配图中已创建的节点
            #print(Pre,Post)
            relation = Relationship(Pre, event_relation[i][1], Post)

            g.create(relation)   #构建关系线


if __name__ == "__main__":
    neo4j_graph = Neo4jGraph()
    node_edges = [['我今天要去餐馆吃饭', 'and', '我要去看电影'], ['电影院会播放电影', 'causality', '我前往电影院'], ['电影院会播放电影', 'causality', '我要去看电影'], ['我坐上了公共交通', 'sequence', '我前往电影院'], ['我前往电影院', 'and', '我看了电影'], ['我看了电影', 'sequence', '我去餐馆吃饭'], ['我去餐馆吃饭', 'sequence', '我坐上公共交通'], ['我坐上公共交通', 'anti_causality', '我必须赶快回家'], ['我坐上公共交通', 'sequence', '我回了家']]
    #print(node_edges[2][0])
    #num = len(node_edges)
    #print(num)
    neo4j_graph.Node_Relation(node_edges)