#-*- coding: utf-8 -*- 
from flask import render_template, request
from app import app,db
from models import player_detail, player_cost, player_fantasypoint
from sqlalchemy.sql.expression import distinct
from sqlalchemy import desc, between
from time import strftime
from app.util.entity import player_point_cost, player_point_time, player_rank
from sqlalchemy.sql.functions import func

@app.route('/')
@app.route('/index')
def index():
    year = strftime("%Y")
    month = strftime("%m")
    day = strftime("%d")
    today = year + "-" + month + "-" + day
    mysession = db.session
    result = mysession.query(player_fantasypoint.date, player_fantasypoint.name, player_fantasypoint.fantasypoint, player_detail.role, player_detail.team).filter_by(date=today).outerjoin(player_detail, player_fantasypoint.name == player_detail.name).order_by(desc(player_fantasypoint.fantasypoint)).all()
    while len(result) == 0:
        day = str(int(day) - 1)
        yesterday = year + "-" + month + "-" + day
        result = mysession.query(player_fantasypoint.date, player_fantasypoint.name, player_fantasypoint.fantasypoint, player_detail.role, player_detail.team).filter_by(date=yesterday).outerjoin(player_detail, player_fantasypoint.name == player_detail.name).order_by(desc(player_fantasypoint.fantasypoint)).all()
    mysession.close()    
    return render_template('index.html', post=result, flag = 'point_rank')
    
@app.route('/point_cost')
def point_cost():
    ppcs = getPointCostList()
    return render_template('index.html', post=ppcs, flag="point_cost")  

@app.route('/point_time')
def point_time():
    ppts = getPointTimeList()
    return render_template('index.html', post=ppts, flag="point_time")    
   
@app.route('/sunsiquan')
def sunsiquan():
    ppcs = getPointCostList()
    ppts = getPointTimeList()
    prs = []
    for ppc in ppcs:
        pr = player_rank()
        name = ppc.name
        index = ppcs.index(ppc)
        index = index + getIndex(ppts, name)
        pr.name = name
        pr.rank = index
        pr.team = ppc.team
        pr.role = ppc.role
        pr.cost = ppc.cost
        prs.append(pr)
    prs.sort()
    return render_template('test.html', post=prs)

@app.route('/addrole')
def addrole():
    #判断是否已经选择球队
    team = request.args.get('team')
    mysession = db.session
    if team is None:
        #选择球队
        teams = mysession.query(distinct(player_detail.team)).all()
        mysession.close()
        return render_template('addrole_teams.html', post=teams)        
    else:
        result = player_detail.query.filter_by(team=team).all()
        mysession.close
        return render_template('addrole.html', post=result)


@app.route('/addcost')
def addcost():
    #判断是否已经选择球队
    team = request.args.get('team')
    mysession = db.session
    if team is None:
        #选择球队
        teams = mysession.query(distinct(player_detail.team)).all()
        mysession.close()
        return render_template('addcost_teams.html', post=teams)   
    else:
        #列出球队中的球员
        result = player_detail.query.filter_by(team=team).all()
        #获取队员的cost
        costs = mysession.query(player_cost).filter(player_cost.name.in_(mysession.query(player_detail.name).filter_by(team=team))).all()
        mysession.close
        return render_template('addcost.html', post=result, costs=costs)

@app.route('/role2db', methods = ['GET', 'POST'])
def role2db():
    name = request.args.get('name')
    role = request.args.get('role')
    mysession = db.session
    player = player_detail.query.filter_by(name=name).first()
    team = player.team
    player.role = role
    mysession.commit()
    mysession.close()
    result = player_detail.query.filter_by(team=team).all()  
    return render_template('addrole.html', post=result)

@app.route('/cost2db', methods = ['GET', 'POST'])
def cost2db():
    team = request.args.get('team')
    mysession = db.session
    for i in range(20):
        name = request.form.get('name' + str(i))
        cost = request.form.get('cost' + str(i))
        if name == '' or cost == '' or name is None or cost is None:
            continue
        player = player_cost.query.filter_by(name=name).first()
        player.cost = cost
        mysession.commit()   
    #获取该队其他队员以便前端展示
    result = player_detail.query.filter_by(team=team).all()  
    #获取队员的cost
    costs = mysession.query(player_cost).filter(player_cost.name.in_(mysession.query(player_detail.name).filter_by(team=team))).all()
    mysession.close
    return render_template('addcost.html', post=result, costs=costs)

def getPointCostList():
    year = strftime("%Y")
    month = strftime("%m")
    day = strftime("%d")
    today = year + "-" + month + "-" + day
    #计算七天前的日期
    lastweek = getLastWeek()
    #取得球员七天内的平均评分以及球员身价
    mysession = db.session
    #result = mysession.query(player_fantasypoint.name, func.avg(player_fantasypoint.fantasypoint), player_cost.cost, player_detail.team, player_detail.role).filter(between(player_fantasypoint.date, lastweek, today)).outerjoin(player_cost, player_fantasypoint.name == player_cost.name).outerjoin(player_detail, player_fantasypoint.name == player_detail.name).group_by(player_fantasypoint.name).all()
    result = mysession.query(player_fantasypoint.name, func.avg(player_fantasypoint.fantasypoint), player_cost.cost, player_detail.team, player_detail.role).filter(between(player_fantasypoint.date, '20170201', today)).outerjoin(player_cost, player_fantasypoint.name == player_cost.name).outerjoin(player_detail, player_fantasypoint.name == player_detail.name).group_by(player_fantasypoint.name).all()
    mysession.close()
    #将获得的数据转换为实体，存放到列表
    ppcs = []
    for r in result:
        ppc = player_point_cost()
        ppc.name = r.name
        ppc.cost = r.cost
        #最近一段时间变成自由球员的球员不用管，直接跳过
        if r.cost is None:
            continue
        #ppc.point_cost = "%.2f%%" % (float(ppc.fantasypoint) / ppc.cost * 100)
        ppc.point_cost = "%.4f" % (float(r[1]) / ppc.cost)
        ppc.team = r.team
        ppc.role = r.role
        ppcs.append(ppc)
    ppcs.sort(reverse=True)
    return ppcs

def getPointTimeList():
    year = strftime("%Y")
    month = strftime("%m")
    day = strftime("%d")
    today = year + "-" + month + "-" + day
    #计算七天前的日期
    lastweek = getLastWeek()
    #取得球员七天内的总评分以及上场时间
    mysession = db.session
    #result = mysession.query(player_fantasypoint.name, func.sum(player_fantasypoint.playtime), func.sum(player_fantasypoint.fantasypoint), player_detail.team, player_detail.role).filter(between(player_fantasypoint.date, lastweek, today)).outerjoin(player_detail, player_fantasypoint.name == player_detail.name).group_by(player_fantasypoint.name).all()
    result = mysession.query(player_fantasypoint.name, func.sum(player_fantasypoint.playtime), func.sum(player_fantasypoint.fantasypoint), player_detail.team, player_detail.role).filter(between(player_fantasypoint.date, '20170201', today)).outerjoin(player_detail, player_fantasypoint.name == player_detail.name).group_by(player_fantasypoint.name).all()
    mysession.close()
    #存入实体player_point_time列表
    ppts = []
    for r in result:
        ppt = player_point_time()
        ppt.name = r.name
        ppt.fantasypoint = r[2]
        ppt.playtime = r[1]
        if ppt.fantasypoint == 0:
            ppt.point_time = "%.4f" % float(0)
        else:
            ppt.point_time = "%.4f" % (float(ppt.fantasypoint) / float(ppt.playtime))
        ppt.team = r.team
        ppt.role = r.role
        ppts.append(ppt)
    ppts.sort(reverse=True)
    return ppts;

def getIndex(list, name):
    for l in list:
        if l.name == name:
            return list.index(l)
        
def getLastWeek():
    year = strftime("%Y")
    month = strftime("%m")
    day = strftime("%d")
    if int(day) > 7:
        day = str(int(day) - 7) 
    #month判定是否为1月; day=day+上个月的天数-7.
    elif month == "01":
        year = str(int(year) - 1) 
        month = "12"
        day = str(int(day) + 31 - 7)
    #month是否为3月，需要进行闰年判定
    elif month == "03":
        month = "02"
        if isRun(int(year)):
            day = str(int(day) + 29 - 7)
        else:
            day = str(int(day) + 28 - 7)
    #一三五七八十腊
    elif is31(month):
        month = str(int(month) - 1)  
        day = str(int(day) + 31 - 7)
    else:
        month = str(int(month) - 1)  
        day = str(int(day) + 30 - 7)  
        
    return year + "-" + month + "-" + day  
        
def isRun(year):
    if (year % 4 == 0) and (year % 100 != 0):
        return True
    elif year % 400 == 0:
        return True
    else:
        return False
def is31(month):
    if month == "2" or month == "4" or month == "6" or month == "8" or month == "9" or month == "11":
        return True
    else:
        return False