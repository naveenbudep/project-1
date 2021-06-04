from swf.models.event import Event

class MarkerEvent(Event):
    # recorded
    decision_task_completed_event_id: int
    # details: str
    marker_name: str

    # record_failed
    cause: str
