from typing import Dict, List

from swf.models.event import Event

class WorkflowExecutionEvent(Event):
    external_initiated_event_id: int
    external_workflow_execution: Dict[str, str]
    # input: str
    signal_name: str

    # cancel_failed
    decision_task_completed_event_id: int

class ChildWorkflowExecutionEvent(Event):
    # start initiated
    child_policy: str
    control: str
    decision_task_completed_event_id: int
    execution_start_to_close_timeout: str
    input: str
    lambda_role: str
    tag_list: List[str]
    task_list: Dict[str, str]  # {name}
    task_priority: str
    task_start_to_close_timeout: str
    workflow_id: str
    workflow_type: Dict[str, str]  # {name, version}

    # failed
    initiated_event_id: int
    started_event_id: int
    details: str
    reason: str
    workflow_execution: Dict[str, str]  # {runId, workflowId}

    # start_failed
    cause: str

    # timeout
    timeout_type: str

class ExternalWorkflowExecutionEvent(Event):
    initiated_event_id: int
    workflow_execution: Dict[str, str]  # {runId, workflowId}

    # signal_execution_initiated
    # control: str
    decision_task_completed_event_id: int
    # input: str
    signal_name: str
    workflow_id: str
    # run_id: str

    # signal_execution_failed
    cause: str
