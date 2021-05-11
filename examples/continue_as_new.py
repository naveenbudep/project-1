from examples.basic import Delay
from simpleflow import Workflow, logger
from simpleflow.canvas import Group
from simpleflow.constants import MINUTE
from simpleflow.swf.task import ContinueAsNewWorkflowTask


class ContinueAsNewWorkflow(Workflow):
    name = "continue_as_new"
    version = "example"
    task_list = "example"
    execution_timeout = 5 * MINUTE

    def run(self, *args, **kwargs):
        while True:
            logger.info(
                "Okay, campers, rise and shine, and don't forget your booties 'cause it's cooooold out there today. "
            )
            logger.info("Context: %s, %s", args, kwargs)
            logger.info("Run context from decider: %s", self.get_run_context())
            timer = self.start_timer("a_timer", 5)
            group = Group()
            group.append(timer)
            group.append(Delay, 5, 0)
            logger.info("Wait... %s", self.submit(group).result)
            task = self.continue_as_new(*args, **kwargs)
            logger.info(
                "Start as new workflow... %s", self.submit(task).result,
            )

    def continue_as_new(self, *args, **kwargs):
        return ContinueAsNewWorkflowTask(self.executor, type(self), *args, **kwargs)
