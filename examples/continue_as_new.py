import datetime

from examples.basic import Delay
from simpleflow import Workflow, logger
from simpleflow.canvas import Group
from simpleflow.constants import MINUTE
from simpleflow.swf.task import ContinueAsNewWorkflowTask


class ContinueAsNewBaseWorkflow(Workflow):
    name = "continue_as_new"

    version = "example"
    task_list = "example"
    execution_timeout = 5 * MINUTE

    def continue_as_new(self, past_history=None, **kwargs):
        return ContinueAsNewWorkflowTask(
            self.executor, type(self), past_history=past_history, **kwargs
        )


class ContinueAsNewWorkflow(ContinueAsNewBaseWorkflow):
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
            group.append(Delay, 7 - i, 0)
            now = datetime.datetime.now()
            logger.info("Wait... %r", self.submit(group).result)
            logger.info("Elapsed: %s", datetime.datetime.now() - now)
            task = self.c_as_n(i=i, **kwargs)
            logger.info(
                "Start as new workflow... %r",
                self.submit(task).result,
            )

    def c_as_n(self, **kwargs):
        return self.continue_as_new(**kwargs)


class ContinueAsNewWorkflowWithHistory(ContinueAsNewWorkflow):
    def c_as_n(self, **kwargs):
        logger.info("c_as_n: kwargs=%r", kwargs)
        return self.continue_as_new(
            past_history=self.executor.history.to_dict(), **kwargs
        )
