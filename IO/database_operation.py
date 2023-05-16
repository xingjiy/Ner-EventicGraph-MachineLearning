import pymongo


class MongoOperation():
    def __init__(self):
        self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        # 新闻数据库
        self.news_db = self.myclient["newsdb"]
        self.news = self.news_db["news"]
        # 事件数据库
        self.event_db = self.myclient["eventdb"]
        self.events = self.event_db["events"]
        self.vector = self.event_db["vectors"]
        # 抽象事件数据库
        self.abstract_event_db = self.myclient["abstractdb"]
        self.abstracts = self.abstract_event_db["abstracts"]

    # 将爬到的新闻放入数据库中
    def news_db_add(self, dataline):
        data = {
            "news_thread": dataline['news_thread'],
            "news_title": dataline['news_title'],
            "news_time": dataline['news_time'],
            "news_text": dataline['news_text'],
            "news_url": dataline['news_url'],
            "news_source": dataline['news_source'],
            "news_source_url": dataline['news_source_url']
        }
        res = self.news.insert_one(data)
        return res

    # 将获得的事件三组元放入数据库中
    def event_db_add(self, datalines):
        datas = list()
        for event_set in datalines:
            events_list_pre = event_set[0]
            events_list_post = event_set[2]
            for event_pre in events_list_pre:
                for event_post in events_list_post:
                    if event_pre and event_post:
                        data = {
                            "pre_event": ''.join(event_pre),
                            "relation": event_set[1],
                            "post_event": ''.join(event_post)
                        }
                        datas.append(data)
        res = self.events.insert_many(datas)#批量插入
        return res

    # 查询并取出数据库中的所有三组元
    def event_db_get(self):
        event_triple_sets = list()
        datas = self.events.find({}, {"id": 0})#查询所有事件前发生的空组
        for data in datas:
            event_triple_set = data["pre_event"] + ',' + data["relation"] + ',' + data["post_event"] #根据前事件、关系、后事件的顺序导入
            event_triple_sets.append(event_triple_set)#依次添加到列表尾部
        return event_triple_sets

    # 将事件和对应的向量存入数据库中
    def vector_db_add(self, datalines):
        datas = list()
        for event in datalines:
            # 感觉其实不用循环……
            datas.append(event)
        res = self.vector.insert_many(datas)
        return res

    # 取出事件向量
    def vector_db_get(self):
        vectors_list = list()
        datas = self.vector.find({}, {"id": 0})
        for data in datas:
            vectors_list.append(data)
        return vectors_list
