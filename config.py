import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):  
    # db SQLLite
    SQLALCHEMY_DATABASE_URI        = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'db_products.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # redis ???   
    REDIS_URL = os.environ['REDIS_URL']

    # mail
    MAIL_SERVER   = 'smtp.rambler.ru'   
    MAIL_PORT     = 465                 
    MAIL_USE_SSL  = True                
    MAIL_USE_TLS  = False               
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')    