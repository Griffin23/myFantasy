#-*- coding: utf-8 -*- 
# 将http response content写入文件请取消以下三行的注释
# import sys
# reload(sys)
# sys.setdefaultencoding( "utf-8" )

import requests, re, sys
from app.util.entity import player
from app import db
from app.models import player_detail, player_fantasypoint, player_cost
from time import strftime
from app.util.timeutil import getLastDayByNum
from sqlalchemy import desc

def getPlayers(response_content):
    #re.S表示可以用.匹配换行符
    name_list = re.findall(r"<td  class =\"normal player_name_out change_color col1 row.+?\"><a class='query_player_name' href='./player/.+?html' target='_blank'>(.+?)</a></td>", response_content, re.S)
    fantasy_point_list = re.findall(r"<td  class =\"current formular change_color col25 row.+?\">(.+?)</td>", response_content, re.S)
    playtime_list = re.findall("<td  class =\"normal mp change_color col6 row.+?\">(.+?)</td>", response_content)
    
    player_list = []
    for i in range(len(name_list)):
        p = player()
        p.name = name_list[i]
        p.fantasy_point = fantasy_point_list[i]
        p.playtime = playtime_list[i]
        player_list.append(p)   
    return player_list
     
def getFromday():
    mysession = db.session
    fromday = mysession.query(player_fantasypoint.date).order_by(desc(player_fantasypoint.date)).limit(1).one()[0]
    mysession.close()
    fromday = ''.join(str(fromday).split('-'))
    return fromday

#应该注意url中的时间为美国时间
def getFantasyPoint():
    fromday = getFromday()
    thisday = strftime("%Y%m%d")
    while True:
        db_day = thisday
        thisday = getLastDayByNum(thisday, 1)
        year = thisday[0:4]
        month = thisday[4:6]
        day = thisday[6:8]
        player_list = []
        for i in range(3):
            url = 'http://www.stat-nba.com/query.php?page=' + str(i) + '&crtcol=formular&order=1&QueryType=game&GameType=season&Formular=ptsaddastmultiply1.5addorbadddrbmultiply0.7addstlmultiply2addblkmultiply1.8substracttovaddfgmultiply0.4substractleftbracketfgasubstractfgrightbracketaddthreepmultiply0.5&PageNum=500&Year0=' + year +'&Month0=' + month +'&Day0=' + day +'&Year1=' + year +'&Month1=' + month +'&Day1=' + day +'#label_show_result'
            r = requests.get(url)
            r.encoding = 'utf-8'
            player_list = player_list + getPlayers(r.text)
        #操作数据库
        mysession = db.session
        for i in range(len(player_list)):
            p = player_fantasypoint(name = player_list[i].name, fantasypoint = player_list[i].fantasy_point, date = db_day, playtime = player_list[i].playtime)
            mysession.add(p)
        mysession.commit()
        if thisday == fromday:
            break
    mysession.close()
    print '\ncomplete!'
    
def getPlayerDetail():
    main_url = "http://www.stat-nba.com/teamList.php"
    r = requests.get(main_url)
    r.encoding = "utf-8"
    team_list = re.findall(r"href=\"./team/(.+?).html\"><img ", r.text)
     
    for i in range(30):
        base_url = "http://www.stat-nba.com/team/" 
        payload = team_list[i] + '.html'
        url = base_url + payload
        r = requests.get(url)
        r.encoding = "utf-8"
        team = re.findall(r"<div class=\"head\">(.+?)\n", r.text)[0].rstrip()
        player_list = re.findall(r"<td colspan=\"1\" class =\"normal player_name change_color col0 row.+?\" rank=\".+?\"><a target='_blank' href='/player/.+?.html'>(.+?)</a></td>", r.text)
        #操作数据库
        mysession = db.session
        for j in range(len(player_list)):
            result = player_detail.query.filter_by(name=player_list[j]).all()
            #判断如果player_detail表中不存在该球员，则新增到数据库
            if len(result) == 0:
                p = player_detail(name = player_list[j], team = team, role = "")
                mysession.add(p)
                mysession.commit()
                c = player_cost(name =  player_list[j], cost = 0)
                mysession.add(c)
        mysession.commit()
        print '.',
    mysession.close()
    print '\ncomplete!'
    
if __name__ == '__main__':
    #getPlayerDetail()
    #getFantasyPoint()
    getFromday()