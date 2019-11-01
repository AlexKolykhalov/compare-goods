from flask            import Flask
from config           import Config
from flask_bootstrap  import Bootstrap
from flask_mail       import Mail
from flask_redis      import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from flask_migrate    import Migrate
# from flask_login        import LoginManager
# from flask_uploads      import UploadSet, IMAGES, configure_uploads

# import dash
# import dash_core_components as dcc
# import dash_html_components as html


bootstrap                                       = Bootstrap()
mail                                            = Mail()
redis_store                                     = FlaskRedis()
db                                              = SQLAlchemy()
migrate                                         = Migrate()
# images                                          = UploadSet('images', IMAGES)
# login_manager                                   = LoginManager()
# login_manager.login_view                        = 'auth.login'
# login_manager.login_message                     = 'Пройдите регистрацию'
# login_manager.login_message_category            = 'alert-info'
# login_manager.refresh_view                      = 'auth.refresh'
# login_manager.needs_refresh_message             = 'Session is closed, please reauthenticate to access this page'
# login_manager.needs_refresh_message_category    = 'alert-info'



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # initialization
    bootstrap.init_app(app)
    mail.init_app(app)
    redis_store.init_app(app, decode_responses=True)
    db.init_app(app)
    migrate.init_app(app, db)

    # login_manager.init_app(app)
        
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app