from app                             import create_app
from app.parcer                      import main_search

from flask                           import current_app
from datetime                        import datetime as dt
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    start = dt.now()
    print('---> Job is start at', start)
    app = create_app()
    with app.app_context():
        main_search()
    end = dt.now()
    print('---> Job is done at', end)

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=7)
# def scheduled_job():
#     print('This job is run every weekday at 7.00')

sched.start()
