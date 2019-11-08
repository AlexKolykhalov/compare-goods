from apscheduler.schedulers.blocking import BlockingScheduler
from parcer import main_search
from datetime import datetime as dt

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=120)
def timed_job():
    start = dt.now()
    main_search()
    end = dt.now()
    print('This job is done.', start,'---', end)

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=7)
# def scheduled_job():
#     print('This job is run every weekday at 7.00')

sched.start()
