import time
from datetime import datetime

import pytz

from simpleflow import Workflow, activity, logger
from simpleflow.canvas import Group
from simpleflow.constants import MINUTE
from simpleflow.swf.task import ContinueAsNewWorkflowTask


@activity.with_attributes(task_list="quickstart", version="example", idempotent=True)
class IdempotentDelay(object):
    def __init__(self, t, x):
        self.t = t
        self.x = x

    def execute(self):
        time.sleep(self.t)
        return self.x


@activity.with_attributes(task_list="quickstart", version="example", idempotent=False)
def datetime_now():
    now = datetime.now(tz=pytz.utc)
    logger.info("datetime_now: %s", now)
    return now.timestamp()


class ContinueAsNewBaseWorkflow(Workflow):
    pass


class ContinueAsNewWorkflow(ContinueAsNewBaseWorkflow):
    name = "continue_as_new"

    version = "example"
    task_list = "example"
    execution_timeout = 5 * MINUTE

    def run(self, *args, **kwargs):
        i = kwargs.get("i", 0)
        while i < 5:
            logger.info(
                "Okay, campers, rise and shine, and don't forget your booties 'cause it's cooooold out there today. "
            )
            logger.info("Context: args=%r, kwargs=%r", args, kwargs)
            logger.info("Run context from decider: %r", self.get_run_context())
            logger.info(
                "Started by: %r", self.executor.history.continued_execution_run_id
            )
            kwargs.pop("i", None)
            i += 1
            timer = self.start_timer("a_timer", 6 - i)
            group = Group()
            group.append(timer)
            group.append(IdempotentDelay, 2, 0)
            start = self.submit(datetime_now).result
            logger.info("Wait... %r", self.submit(group).result)
            end = self.submit(datetime_now).result
            logger.info("Elapsed: %s", end - start)
            task = self.c_as_n(i=i, **kwargs)
            logger.info("Start as new workflow...")
            self.submit(task).wait()

    def continue_as_new(self, keep_history=False, **kwargs):
        return ContinueAsNewWorkflowTask(
            self.executor, type(self), keep_history=keep_history, **kwargs
        )

    def c_as_n(self, **kwargs):
        return self.continue_as_new(**kwargs)


class ContinueAsNewWorkflowWithHistory(ContinueAsNewWorkflow):
    name = "continue_as_new_with_history"

    def c_as_n(self, **kwargs):
        return self.continue_as_new(keep_history=True, **kwargs)
