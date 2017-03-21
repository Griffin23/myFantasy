class player():
    name = ''
    fantasy_point = 0
    playtime = 0
    
class player_rank():
    rank = ''
    name = ''
    team = ''
    role = ''
    cost = ''
    
    def __lt__(self, other):  
        return self.rank < other.rank  
    
    
class player_point_cost():
    name = ''
    cost = ''
    point_cost = ''
    team = ''
    role = ''
    
    def __lt__(self, other):  
        return self.point_cost < other.point_cost  

class player_point_time():
    name = ''
    fantasypoint = ''
    playtime = ''
    point_time = ''
    team = ''
    role = ''
    
    def __lt__(self, other):  
        return self.point_time < other.point_time
    
class player_point_forecast():
    name = ''
    fantasypoint = ''
    playtime = ''
    team = ''
    role = ''
    
    def __lt__(self, other):  
        return self.fantasypoint < other.fantasypoint