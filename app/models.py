from app import db


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

class News(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    html_news         = db.Column(db.String)
    date_news         = db.Column(db.DateTime())

# class Lenta(db.Model):
#     id                = db.Column(db.Integer, primary_key=True)
#     html_lenta        = db.Column(db.String)
#     date_lenta        = db.Column(db.DateTime())

# class Perekrestok(db.Model):
#     id                = db.Column(db.Integer, primary_key=True)
#     html_perekrestok  = db.Column(db.String)
#     date_perekrestok  = db.Column(db.DateTime())

# class Pka(db.Model):
#     id                = db.Column(db.Integer, primary_key=True)
#     html_pka          = db.Column(db.String)
#     date_pka          = db.Column(db.DateTime())