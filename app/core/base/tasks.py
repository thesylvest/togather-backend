from datetime import datetime
from typing import Callable
import asyncio


def run_async_task(func: Callable, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func(*args, **kwargs))


def schedule_task(func: Callable, time: datetime, *args, **kwargs):
    if datetime.now() == time:
        func(*args, **kwargs)
# TODO: cant use celery as it is not recommended for far future
# cant use apschedule as it is not recommended for far future
# implement a manual cronjob for this if possible use BackgroundTask
