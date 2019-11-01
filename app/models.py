from app import db


class Sku(db.Model):
    id                = db.Column(db.String(12), primary_key=True)
    sku_category      = db.Column(db.Integer)
    sku_name          = db.Column(db.String(100))
    sku_lowercase     = db.Column(db.String(100), index=True)
    sku_price_asc     = db.Column(db.Integer)
    sku_price_desc    = db.Column(db.Integer)
    sku_discount_desc = db.Column(db.Integer)
    sku_html_1        = db.Column(db.String)
    sku_html_2        = db.Column(db.String)
    sku_html_3        = db.Column(db.String)
    sku_type          = db.Column(db.String(5))
    sku_twin          = db.Column(db.Boolean, default=False)

class News(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    html_news         = db.Column(db.String)
    date_news         = db.Column(db.DateTime()) 