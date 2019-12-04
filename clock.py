from app                             import create_app
from app.parcer                      import main_search, get_news

from flask                           import current_app
from datetime                        import datetime as dt
from apscheduler.schedulers.blocking import BlockingScheduler

import requests

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=2)
def timed_job():
    start = dt.now()
    print('------> Job start at:', start)
    requests.get('https://compare-goods.herokuapp.com/')    
    app = create_app()
    with app.app_context():
        get_news()
        # main_search()
    end = dt.now()
    print('------> Job done at:', end)

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=7)
# def scheduled_job():
#     print('This job is run every weekday at 7.00')

sched.start()
