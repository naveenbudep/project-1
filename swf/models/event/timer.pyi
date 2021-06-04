from swf.models.event import Event

class TimerEvent(Event):
    # started
    # control: str
    decision_task_completed_event_id: int
    start_to_fire_timeout: str
    timer_id: str

    # start_failed
    cause: str
