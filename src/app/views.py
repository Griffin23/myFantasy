#-*- coding: utf-8 -*- 
from flask import render_template, request, session
from app import app,db
from models import player_detail, player_cost, player_fantasypoint
from sqlalchemy.sql.expression import distinct, and_
from sqlalchemy import desc, between
from app.util import timeutil
from app.util import randomcodeUtil
from app.util.entity import player_point_cost, player_point_time, player_rank,\
    player_point_forecast
from sqlalchemy.sql.functions import func
import StringIO
from app.util.mailutil import sendMail

@app.route('/')
@app.route('/index')
def index():
    today = timeutil.getToday()
    mysession = db.session
    result = mysession.query(player_fantasypoint.date, player_fantasypoint.name, player_fantasypoint.fantasypoint, player_detail.role, player_detail.team).filter_by(date=today).outerjoin(player_detail, player_fantasypoint.name == player_detail.name).order_by(desc(player_fantasypoint.fantasypoint)).all()
    lastday = today
    while len(result) == 0:
        lastday = timeutil.getLastDayByNum(lastday, 1)
        result = mysession.query(player_fantasypoint.date, player_fantasypoint.name, player_fantasypoint.fantasypoint, player_detail.role, player_detail.team).filter_by(date=lastday).outerjoin(player_detail, player_fantasypoint.name == player_detail.name).order_by(desc(player_fantasypoint.fantasypoint)).all()
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

@app.route('/point_forecast')
def point_forecast():
#     ppfs = getPointForecastList()
#     for ppf in ppfs:
#         ppf.fantasypoint = "%.1f" % ppf.fantasypoint
#     return render_template('index.html', post=ppfs, flag="point_forecast")
    return render_template('forecast.html')
    
@app.route('/suggest')  
def suggest():
    return render_template('index.html', flag="suggest") 
   
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

@app.route('/sendmail', methods = ['POST'])
def sendmail():
    email =  request.form.get('email')
    suggestion = request.form.get('suggestion')
    userRandomCode = request.form.get('randomCode')
    imgRandomCode = session['randomCode']
    
    #校验验证码是否正确
    if userRandomCode.upper() != imgRandomCode.upper():
        return render_template('index.html', flag="suggest", randomCode="0")
    else:
        fromMail = email
        subject = 'Fantasy留言建议'
        content = suggestion
        sendMail(fromMail, subject, content)
        return render_template('index.html', flag="suggest", randomCode="1")

@app.route('/getrandomcode<regex("[0-9]*"):salt>')
def getrandomcode(salt):
    createImg_result = randomcodeUtil.create_validate_code()
    code_img = createImg_result[0]
    session['randomCode'] = createImg_result[1]
    buf = StringIO.StringIO()
    code_img.save(buf,'JPEG') 
    buf_str = buf.getvalue() 
    response = app.make_response(buf_str)
    response.headers['Content-Type'] = 'image/jpeg'
    return response

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
    today = timeutil.getToday()
    #计算两周前的日期
    last2week = timeutil.getLastDayByNum(today, 14)
    #取得球员两周内的平均评分以及球员身价
    mysession = db.session
    result = mysession.query(player_fantasypoint.name, func.avg(player_fantasypoint.fantasypoint), player_cost.cost, player_detail.team, player_detail.role).filter(between(player_fantasypoint.date, last2week, today)).outerjoin(player_cost, player_fantasypoint.name == player_cost.name).outerjoin(player_detail, player_fantasypoint.name == player_detail.name).group_by(player_fantasypoint.name).all()
    #result = mysession.query(player_fantasypoint.name, func.avg(player_fantasypoint.fantasypoint), player_cost.cost, player_detail.team, player_detail.role).filter(between(player_fantasypoint.date, '20170201', today)).outerjoin(player_cost, player_fantasypoint.name == player_cost.name).outerjoin(player_detail, player_fantasypoint.name == player_detail.name).group_by(player_fantasypoint.name).all()
    #将获得的数据转换为实体，存放到列表
    ppcs = []
    for r in result:
        ppc = player_point_cost()
        ppc.name = r.name
        ppc.cost = r.cost
        #最近一段时间变成自由球员的球员不用管，直接跳过
        if r.cost is None:
            continue
        ppc.point_cost = "%.4f" % (float(r[1]) / ppc.cost)
        ppc.team = r.team
        ppc.role = r.role
        ppcs.append(ppc)
    ppcs.sort(reverse=True)
    mysession.close()
    return ppcs

def getPointTimeList():
    today = timeutil.getToday()
    #计算两周前的日期
    last2week = timeutil.getLastDayByNum(today, 14)
    #取得球员两周内的总评分以及上场时间
    mysession = db.session
    result = mysession.query(player_fantasypoint.name, func.sum(player_fantasypoint.playtime), func.sum(player_fantasypoint.fantasypoint), player_detail.team, player_detail.role, player_cost.cost).filter(between(player_fantasypoint.date, last2week, today)).outerjoin(player_detail, player_fantasypoint.name == player_detail.name).outerjoin(player_cost, player_fantasypoint.name == player_cost.name).group_by(player_fantasypoint.name).all()
    #result = mysession.query(player_fantasypoint.name, func.sum(player_fantasypoint.playtime), func.sum(player_fantasypoint.fantasypoint), player_detail.team, player_detail.role).filter(between(player_fantasypoint.date, '20170201', today)).outerjoin(player_detail, player_fantasypoint.name == player_detail.name).group_by(player_fantasypoint.name).all()
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
        ppt.cost = r.cost
        ppts.append(ppt)
    ppts.sort(reverse=True)
    return ppts;

def getPointForecastList():
    today = timeutil.getToday()
    #计算两周前的日期
    last2week = timeutil.getLastDayByNum(today, 14)
    #获取球员列表
    mysession = db.session
    player_list = mysession.query(player_detail).filter(player_detail.role!='').all()
    ppfs = []
    game_record = []
    for player in player_list:
        ppf = player_point_forecast()
        name = player.name
        game_record = mysession.query(player_fantasypoint.name, player_fantasypoint.fantasypoint, player_fantasypoint.date, player_fantasypoint.playtime, player_detail.team, player_detail.role).filter(and_(between(player_fantasypoint.date, last2week, today), player_fantasypoint.name==name)).outerjoin(player_detail, player_detail.name == name).all()
        if len(game_record) < 5:
            continue
        fantasypoint_list = []
        playtime_list = []
        for g in game_record:
            fantasypoint_list.append(g.fantasypoint)
            playtime_list.append(g.playtime)
        ppf.name = name
        ppf.role = game_record[0].role
        ppf.team = game_record[0].team
        result = getPointForecast(fantasypoint_list, playtime_list)
        ppf.fantasypoint = result[0]
        ppf.playtime = int(result[1])
        ppfs.append(ppf)
    ppfs.sort(reverse=True)
    mysession.close()
    return ppfs

#线性回归预测    
def getPointForecast(fantasypoint_list, playtime_list):
    length = len(playtime_list)
    sum_x = 0
    sum_playtime = 0
    sum_fantasypoint = 0
    #param1 = x1y1 + x2y2 + ... + xnyn
    param1 = 0
    #param2 = x1^2 + x2^2 + ... + xn^2
    param2 = 0
    for i in range(length):
        fantasypoint = fantasypoint_list[i]
        x = i + 1
        playtime = playtime_list[i]
        sum_fantasypoint = sum_fantasypoint + fantasypoint
        sum_x = sum_x + x
        sum_playtime = sum_playtime + playtime
        param1 = param1 + x * playtime
        param2 = param2 + x * x
    avg_x = float(sum_x) / length
    avg_playtime = float(sum_playtime) / length
    #y = bx + a
    b = float((param1 - length * avg_x * avg_playtime)) / (param2 - length * avg_x * avg_x)
    a = avg_playtime - b * avg_x
    playtime_forecast = b * (length + 1) + a
    point_time = (float(sum_fantasypoint) / float(sum_playtime))
    fantasypoint_forecast = playtime_forecast * point_time 
    return fantasypoint_forecast, playtime_forecast
    
def getIndex(list, name):
    for l in list:
        if l.name == name:
            return list.index(l)