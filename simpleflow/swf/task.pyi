from typing import Any, Dict, List, Optional, Tuple, Type, Union

from simpleflow import Activity, Workflow, task
from simpleflow.swf.executor import Executor
from swf.models import ActivityType, Domain, WorkflowType
from swf.models.decision.base import Decision

class SwfTask:
    @property
    def payload(self) -> Any: ...

class ActivityTask(task.ActivityTask, SwfTask):
    cached_models: Dict[Tuple[str, str, str], ActivityType]
    @classmethod
    def from_generic_task(cls, task: ActivityTask) -> ActivityTask: ...
    @property
    def payload(self) -> Activity: ...
    @property
    def task_list(self) -> str: ...
    def schedule(
        self, domain: Domain, task_list: Optional[str] = None, **kwargs
    ) -> List[Decision]: ...
    def get_input(self) -> Dict: ...
    @classmethod
    def get_activity_type(
        cls, domain: Domain, name: str, version: str
    ) -> ActivityType: ...

class NonPythonicActivityTask(ActivityTask):
    def get_input(self) -> Union[Dict, List]: ...

class WorkflowTask(task.WorkflowTask, SwfTask):
    cached_models: Dict[Tuple[str, str, str], WorkflowType]
    @property
    def name(self) -> str: ...
    @property
    def payload(self) -> Type[Workflow]: ...
    @property
    def tag_list(self) -> None: ...
    @property
    def task_list(self) -> str: ...
    def get_input(self) -> Dict[str, Union[Dict[str, Any], List[Any]]]: ...
    def schedule(
        self,
        domain: Domain,
        task_list: Optional[str] = None,
        executor: Optional[Executor] = None,
        **kwargs
    ) -> List[Decision]: ...
    @classmethod
    def get_workflow_type(
        cls, domain: Domain, name: str, version: str
    ) -> WorkflowType: ...

class ContinueAsNewWorkflowTask(WorkflowTask):
    keep_history: bool
    # def __init__(
    #     self,
    #     executor: Optional[Executor],
    #     workflow: Type[Workflow],
    #     keep_history: bool = False,
    #     *args,
    #     **kwargs
    # ): ...
    def schedule(
        self,
        domain: Domain,
        task_list: Optional[str] = None,
        executor: Executor = None,
        **kwargs
    ) -> List[Decision]: ...

class SignalTask(task.SignalTask, SwfTask):
    idempotent: bool = True
    workflow_id: str
    run_id: str
    control: Optional[Dict]
    extra_input: Optional[Dict]
    @classmethod
    def from_generic_task(
        cls,
        a_task: task.SignalTask,
        workflow_id: str,
        run_id: str,
        control: Optional[Dict],
        extra_input: Optional[Dict],
    ) -> SignalTask: ...
    def schedule(self, *args, **kwargs) -> List[Decision]: ...

class MarkerTask(task.MarkerTask, SwfTask):
    idempotent: bool = True
    @classmethod
    def from_generic_task(cls, a_task: task.MarkerTask) -> MarkerTask: ...

class TimerTask(task.TimerTask, SwfTask):
    idempotent: bool = True
    @classmethod
    def from_generic_task(cls, a_task: task.TimerTask) -> TimerTask: ...
    def schedule(self, *args, **kwargs) -> List[Decision]: ...

class CancelTimerTask(task.CancelTimerTask, SwfTask):
    idempotent: bool = True
    @classmethod
    def from_generic_task(cls, a_task: task.CancelTimerTask) -> TimerTask: ...
    def schedule(self, *args, **kwargs) -> List[Decision]: ...
