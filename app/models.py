from app         import db, login_manager
from flask_login import UserMixin



class Sku(db.Model):
    id                = db.Column(db.String(12), primary_key=True)
    sku_category      = db.Column(db.Integer)
    sku_name          = db.Column(db.String(200))
    sku_lowercase     = db.Column(db.String(200), index=True)
    sku_price_asc     = db.Column(db.Numeric(7,2))
    sku_price_desc    = db.Column(db.Numeric(7,2))
    sku_discount_desc = db.Column(db.Integer)
    sku_html_1        = db.Column(db.String)
    sku_html_2        = db.Column(db.String)
    sku_html_3        = db.Column(db.String)    
    sku_twin          = db.Column(db.Boolean, default=False)

class Users(db.Model, UserMixin):
    id                = db.Column(db.String(24), primary_key=True)
    heart_productsId  = db.Column(db.String)
    visit_time        = db.Column(db.DateTime())

class News(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    html_news         = db.Column(db.String)
    date_news         = db.Column(db.DateTime())

class DbStatus(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    status            = db.Column(db.String(1))

# initialize User
@login_manager.user_loader
def load_user(userId):
    return Users.query.get(userId)