import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):  
    # db SQLLite
    SQLALCHEMY_DATABASE_URI        = os.environ.get('DATABASE_URL') or 'postgresql:///db_products'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # redis ???   
    # REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/1'

    # mail
    MAIL_SERVER   = 'smtp.rambler.ru'   
    MAIL_PORT     = 465                 
    MAIL_USE_SSL  = True                
    MAIL_USE_TLS  = False               
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')    