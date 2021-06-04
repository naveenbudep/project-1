from typing import Dict

from swf.models.event import Event

class ActivityTaskEvent(Event):
    scheduled_event_id: int
    decision_task_completed_event_id: int
    activity_id: str
    activity_type: Dict[str, str]  # {name, version}
    task_list: Dict[str, str]  # {name}

    # started
    # identity: str

    # schedule_failed
    cause: str

    # timeout
    timeout_type: str

class DecisionTaskEvent(Event):
    _type = "DecisionTask"
