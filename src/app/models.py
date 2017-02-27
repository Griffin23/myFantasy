from app import db

class player_detail(db.Model):
        pdid = db.Column(db.Integer, primary_key = True)
        name = db.Column(db.String(45), unique = True)
        team = db.Column(db.String(45))
        role = db.Column(db.String(5))
        
class player_fantasypoint(db.Model):
        name = db.Column(db.String(45), primary_key = True)
        fantasypoint = db.Column(db.Float)
        date = db.Column(db.Date)
        playtime = db.Column(db.Integer)
        
class player_cost(db.Model):
        name = db.Column(db.String(45), primary_key = True)
        cost = db.Column(db.Integer)