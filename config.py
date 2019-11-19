import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):  
    # db Postgresql
    SQLALCHEMY_DATABASE_URI        = os.environ.get('DATABASE_URL') or 'postgresql:///db_products'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # redis ???   
    # REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/1'

    # #algoliasearch
    # ALGOLIASEARCH_APP_ID  = os.environ.get('ALGOLIASEARCH_APP_ID')
    # ALGOLIASEARCH_API_KEY = os.environ.get('ALGOLIASEARCH_API_KEY')

    # mail
    MAIL_SERVER   = 'smtp.rambler.ru'   
    MAIL_PORT     = 465                 
    MAIL_USE_SSL  = True                
    MAIL_USE_TLS  = False               
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')    