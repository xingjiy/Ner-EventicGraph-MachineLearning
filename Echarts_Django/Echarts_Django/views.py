import json
from py2neo import *
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
# def index(request):
#     views_name = "菜鸟教程"
#     context = {}
#     context['hello'] = 'Hello World!'
#     return render(request, 'index.html', {"name":views_name})

# 连接数据库
graph = Graph('http://localhost:7474/', auth=('neo4j', 'test'))

def majorityCnt(classList):
    classCount = {}
    #  统计列表中元素出现的次数，并存储在字典中
    for vote in classList:
        if vote not in classCount:
            classCount[vote] = 0
        classCount[vote] += 1
    sortedClassCount = sorted(classCount.items(),key = lambda e:e[1], reverse=True)
    #  返回出现次数最多的元素
    result = []
    for i in range(0, 7):
        result.append(sortedClassCount[i][0])
    return result

def cout_sort():
    # 查询所有节点关系
    reps = graph.run('MATCH(n)-[rel]->(m) return rel').data()
    # 定义数组存储节点信息
    links = []
    # 处理关系信息
    print(len(reps))
    for r in reps:
        source = str(r['rel'].start_node['name'])
        target = str(r['rel'].end_node['name'])
        name = str(type(r['rel']).__name__)
        links.append(source)
        links.append(target)
    result = majorityCnt(links)
    return result

def search_one_all(value):
    # 定义data数组存储节点信息
    data = []
    # 定义links数组存储关系信息
    links = []
    # 查询节点是否存在
    node = graph.run('MATCH(n:event{name:"' + value + '"}) return n LIMIT 1500').data()
    # 如果节点存在len(node)的值为1不存在的话len(node)的值为0
    if len(node):
        # 如果该节点存在将该节点存入data数组中
        # 构造字典存放节点信息
        dict1 = {
            'name': value,
            'symbolSize': 50,
            'category': '事件'
        }
        data.append(dict1)
        # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
        nodes = graph.run('MATCH(n:event{name:"' + value + '"})<-[rel * 1..3]->(m) return m LIMIT 1500').data()
        # 查询该节点所涉及的所有relationship，无向，步长为1，并返回这些relationship
        reps = graph.run('match (n :event{name:"' + value + '"}) <- [rel * 1..3]->(m) return rel LIMIT 1500').data()
        # 处理节点信息
        for n in nodes:
            # 将节点信息的格式转化为json
            node = json.dumps(n, ensure_ascii=False)
            node = json.loads(node)
            # 取出节点信息中person的name
            name = str(node['m']['name'])
            # 构造字典存放单个节点信息
            dict1 = {
                'name': name,
                'symbolSize': 50,
                'category': '事件'
            }
            # 将单个节点信息存储进data数组中
            data.append(dict1)
        data = [dict(t) for t in {tuple(d.items()) for d in data}]
        for r in reps:
            for i in range(len(r["rel"])):
                source = str(r['rel'][i].start_node['name'])
                target = str(r['rel'][i].end_node['name'])
                name = str(type(r['rel'][i]).__name__)
                dict1 = {
                    'source': source,
                    'target': target,
                    'name': name
                }
                links.append(dict1)
        # 构造字典存储data和links
        search_neo4j_data = {
            'data': data,
            'links': links
        }
        # 将dict转化为json格式
        search_neo4j_data = json.dumps(search_neo4j_data)
        return search_neo4j_data
    else:
        print("查无此事件")
        return 0

def search_one(value):
    # 定义data数组存储节点信息
    data = []
    # 定义links数组存储关系信息
    links = []
    # 查询节点是否存在
    node = graph.run('MATCH(n:event{name:"' + value + '"}) return n LIMIT 1500').data()
    # 如果节点存在len(node)的值为1不存在的话len(node)的值为0
    if len(node):
        # 如果该节点存在将该节点存入data数组中
        # 构造字典存放节点信息
        dict = {
            'name': value,
            'symbolSize': 50,
            'category': '事件'
        }
        data.append(dict)
        # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
        nodes = graph.run('MATCH(n:event{name:"' + value + '"})<-->(m:event) return m LIMIT 1500').data()
        # 查询该节点所涉及的所有relationship，无向，步长为1，并返回这些relationship
        reps = graph.run('MATCH(n:event{name:"' + value + '"})<-[rel]->(m:event) return rel LIMIT 1500').data()
        # 处理节点信息
        for n in nodes:
            # 将节点信息的格式转化为json
            node = json.dumps(n, ensure_ascii=False)
            node = json.loads(node)
            # 取出节点信息中person的name
            name = str(node['m']['name'])
            # 构造字典存放单个节点信息
            dict = {
                'name': name,
                'symbolSize': 50,
                'category': '事件'
            }
            # 将单个节点信息存储进data数组中
            data.append(dict)
        # 处理relationship
        for r in reps:
            source = str(r['rel'].start_node['name'])
            target = str(r['rel'].end_node['name'])
            name = str(type(r['rel']).__name__)
            dict = {
                'source': source,
                'target': target,
                'name': name
            }
            links.append(dict)
        # 构造字典存储data和links
        search_neo4j_data = {
            'data': data,
            'links': links
        }
        # 将dict转化为json格式
        search_neo4j_data = json.dumps(search_neo4j_data)
        return search_neo4j_data
    else:
        print("查无此事件")
        return 0

def grapy_page(request):
    ctx = {}
    if request.method == 'POST':
        # 接收前端传过来的查询值
        node_name = request.POST.get('node')
        # 推荐结果
        cout_sort_data = ' '.join(cout_sort())
        # 查询结果
        search_neo4j_data = search_one_all(node_name)
        search_neo4j_one_data = search_one(node_name)
        # 将查询结果传给前端
        if search_neo4j_data == 0:
            ctx = {'title': '数据库中暂未添加该实体'}
        # 查询到了该节点
        else:
            return render(request, 'grapy.html',
                          {'search_neo4j_data': search_neo4j_data, 'ctx': ctx, "node_name": node_name,
                           "search_neo4j_one_data": search_neo4j_one_data,"cout_sort_data": cout_sort_data})

    return render(request, 'grapy.html', {'ctx': ctx, })

def home(request):
    # 推荐结果
    cout_sort_data = ' '.join(cout_sort())
    return render(request, 'home.html', {"cout_sort_data": cout_sort_data})

# 用户登录
def logins(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username,password=password)
        # 用authenticate判断用户名密码是否正确
        if user:
            login(request,user)
            return redirect('/home/')
        else:
            msg='用户名密码错误！'
            return render(request,'login.html',locals())
    return render(request,'login.html')

# 用户注册
def regist(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        email = request.POST.get("email")
        if password != password2:
            msg='两次输入的密码不一样！'
            return render(request,'regist.html',locals())
        elif username == '':
            msg='用户名不能为空'
            return render(request,'regist.html',locals())
        cuser = User.objects.create_user(username=username,password=password,email=email)
        cuser.save()
        return redirect('/login/')
    return render(request,'regist.html')

# 登出
def log_out(request):
    logout(request)
    return redirect('/')

def index(request):
    return render(request, 'index.html')

if __name__ == '__main__':
    # print(search_one('豆油库存增长'))
    # print(type(search_one_all('豆油库存增长')))
    # print([search_one_all('豆油库存增长')][0])
    print(cout_sort())
    cout_sort_neo4j = ','.join(cout_sort())
    print(cout_sort_neo4j)