import collections
from typing import TYPE_CHECKING

import swf.models.event
import swf.models.history
from simpleflow import logger

if TYPE_CHECKING:
    from typing import (
        Any,
        AnyStr,
        DefaultDict,
        Dict,
        List,
        Optional,
        OrderedDict,
        Union,
    )


def g_attr(event, s):
    return getattr(event, s, None)


class History(object):
    """
    History data.

    :ivar _history: raw(ish) history events
    :ivar _activities: activity events
    :ivar _child_workflows: child workflow events
    :ivar _external_workflows_signaling: external workflow signaling events, by initiated event ID
    :ivar _external_workflows_canceling: external workflow canceling events
    :ivar _signals: activity events
    :ivar _markers: marker events
    :ivar _timers: timer events
    :ivar _tasks: ordered list of tasks/etc
    """

    def __init__(
        self,
        history,  # type: Optional[swf.models.history.History]
    ):
        # type: (...) -> None
        self._history = history
        self._activities = (
            collections.OrderedDict()
        )  # type: OrderedDict[AnyStr, dict[str, Any]]
        self._child_workflows = (
            collections.OrderedDict()
        )  # type: OrderedDict[AnyStr, Dict[AnyStr, Any]]
        self._external_workflows_signaling = (
            collections.OrderedDict()
        )  # type: OrderedDict[int, Dict[AnyStr, Any]]
        self._external_workflows_canceling = (
            collections.OrderedDict()
        )  # type: OrderedDict[AnyStr, Dict[AnyStr, Any]]
        self._signals = (
            collections.OrderedDict()
        )  # type: OrderedDict[AnyStr, Dict[AnyStr, Any]]
        self._signaled_workflows = collections.defaultdict(
            list
        )  # type: DefaultDict[List[Dict[AnyStr, Any]]]
        self._markers = (
            collections.OrderedDict()
        )  # type: OrderedDict[AnyStr, List[Dict[AnyStr, Any]]]
        self._timers = {}  # type: Dict[AnyStr, Dict[AnyStr, Any]]
        self._tasks = []  # type: List[Dict[AnyStr, Any]]
        self._cancel_requested = None  # type: Optional[Dict[AnyStr, Any]]
        self._cancel_failed = None  # type: Optional[Dict[AnyStr, Any]]
        self.started_decision_id = None  # type: Optional[int]
        self.completed_decision_id = None  # type: Optional[int]
        self.continued_execution_run_id = None  # type: Optional[AnyStr]

    def to_dict(self):
        # type: () -> Dict[AnyStr, Any]
        return {
            "activities": self.activities,
            "child_workflows": self.child_workflows,
            "external_workflows_signaling": self.external_workflows_signaling,
            "external_workflows_canceling": self.external_workflows_canceling,
            "signals": self.signals,
            "signaled_workflows": self.signaled_workflows,
            "markers": self.markers,
            "timers": self.timers,
            "tasks": self.tasks,
            "cancel_requested": self.cancel_requested,
            "cancel_failed": self.cancel_failed,
            "started_decision_id": self.started_decision_id,
            "completed_decision_id": self.completed_decision_id,
            "continued_execution_run_id": self.continued_execution_run_id,
        }

    @classmethod
    def from_dict(
        cls,
        d,  # type: Dict[AnyStr, Any]
    ):
        hist = cls(None)
        hist._activities = d["activities"]
        hist._child_workflows = d["child_workflows"]
        hist._external_workflows_signaling = d["external_workflows_signaling"]
        hist._external_workflows_canceling = d["external_workflows_canceling"]
        hist._signals = d["signals"]
        hist._signaled_workflows = d["signaled_workflows"]
        hist._markers = d["markers"]
        hist._timers = d["timers"]
        hist._tasks = d["tasks"]
        hist._cancel_requested = d["cancel_requested"]
        hist._cancel_failed = d["cancel_failed"]
        hist.started_decision_id = d["started_decision_id"]
        hist.completed_decision_id = d["completed_decision_id"]
        hist.continued_execution_run_id = d["continued_execution_run_id"]
        return hist

    @property
    def swf_history(self):
        # type: () -> Optional[swf.models.history.History]
        """
        :return: SWF history
        """
        return self._history

    @property
    def activities(self):
        # type: () -> OrderedDict[AnyStr, Dict[AnyStr, Any]]
        """
        :return: activities
        """
        return self._activities

    @property
    def child_workflows(self):
        # type: () -> OrderedDict[AnyStr, Dict[AnyStr, Any]]
        """
        :return: child WFs
        """
        return self._child_workflows

    @property
    def external_workflows_signaling(self):
        # type: () -> OrderedDict[int, Dict[AnyStr, Any]]
        """
        :return: external WFs
        """
        return self._external_workflows_signaling

    @property
    def external_workflows_canceling(self):
        # type: () -> OrderedDict[int, Dict[AnyStr, Any]]
        """
        :return: external WFs
        """
        return self._external_workflows_canceling

    @property
    def signals(self):
        # type: () -> OrderedDict[AnyStr, Dict[AnyStr, Any]]
        """
        :return: signals
        """
        return self._signals

    @property
    def cancel_requested(self):
        # type: () -> Optional[Dict[AnyStr, Any]]
        """
        :return: Last cancel requested event, if any.
        """
        return self._cancel_requested

    @property
    def cancel_failed(self):
        # type: () -> Optional[Dict[AnyStr, Any]]
        """
        :return: Last cancel failed event, if any.
        """
        return self._cancel_failed

    @property
    def cancel_requested_id(self):
        # type: () -> Optional[int]
        """
        :return: ID of last cancel requested event, if any.
        """
        return self._cancel_requested["event_id"] if self._cancel_requested else None

    @property
    def cancel_failed_decision_task_completed_event_id(self):
        # type: () -> Optional[int]
        """
        :return: ID of last cancel failed event, if any.
        """
        return (
            self._cancel_failed["decision_task_completed_event_id"]
            if self._cancel_failed
            else None
        )

    @property
    def signaled_workflows(self):
        # type: () -> DefaultDict[List[Dict[AnyStr, Any]]]
        """
        :return: signaled workflows
        """
        return self._signaled_workflows

    @property
    def markers(self):
        # type: () -> OrderedDict[AnyStr, List[Dict[AnyStr, Any]]]
        return self._markers

    @property
    def timers(self):
        # type: () -> Dict[str, Dict[AnyStr, Any]]
        return self._timers

    @property
    def tasks(self):
        # type: () -> List[Dict[AnyStr, Any]]
        return self._tasks

    @property
    def events(self):
        # type: () -> Optional[List[swf.models.event.Event]]
        return self._history.events if self._history else None

    def parse_activity_event(
        self,
        events,  # type: List[Union[swf.models.event.Event, swf.models.event.ActivityTaskEvent]]
        event,  # type: swf.models.event.ActivityTaskEvent
    ):
        # type: (...) -> None
        """
        Aggregate all the attributes of an activity in a single entry.
        """

        def get_activity():
            # type: () -> Dict[AnyStr, Any]
            """
            Return a reference to the corresponding activity.
            :return: mutable activity
            """
            scheduled_event = events[
                event.scheduled_event_id - 1
            ]  # type: swf.models.event.ActivityTaskEvent
            return self._activities[scheduled_event.activity_id]

        activity_id = event.activity_id
        if event.state == "scheduled":
            activity = {
                "type": "activity",
                "id": activity_id,
                "name": event.activity_type["name"],
                "version": event.activity_type["version"],
                "state": event.state,
                "scheduled_id": event.id,
                "scheduled_timestamp": event.timestamp,
                "input": event.input,
                "task_list": event.task_list["name"],
                "control": event.control,
                "decision_task_completed_event_id": event.decision_task_completed_event_id,
                "task_priority": g_attr(event, "task_priority"),
            }
            if activity_id not in self._activities:
                self._activities[activity_id] = activity
                self._tasks.append(activity)
            else:
                # When the executor retries a task, it schedules it again.
                # We have to take care of not overriding some values set by the
                # previous execution of the task such as the number of retries
                # in ``retry``.  As the state of the event mutates, it
                # corresponds to the last execution.
                self._activities[activity_id].update(activity)
        elif event.state == "schedule_failed":
            activity = {
                "state": event.state,
                "cause": event.cause,
                "schedule_failed_timestamp": event.timestamp,
            }

            if activity_id not in self._activities:
                activity.update(
                    {
                        "type": "activity",
                        "id": activity_id,
                        "name": event.activity_type["name"],
                        "version": event.activity_type["version"],
                        "decision_task_completed_event_id": event.decision_task_completed_event_id,
                    }
                )
                self._activities[activity_id] = activity
                self._tasks.append(activity)
            else:
                # When the executor retries a task, it schedules it again.
                # We have to take care of not overriding some values set by the
                # previous execution of the task such as the number of retries
                # in ``retry``.  As the state of the event mutates, it
                # corresponds to the last execution.
                self._activities[activity_id].update(activity)

        elif event.state == "started":
            activity = get_activity()
            activity.update(
                {
                    "state": event.state,
                    "identity": g_attr(event, "identity"),
                    "started_id": event.id,
                    "started_timestamp": event.timestamp,
                }
            )
        elif event.state == "completed":
            activity = get_activity()
            activity.update(
                {
                    "state": event.state,
                    "result": g_attr(event, "result"),
                    "completed_id": event.id,
                    "completed_timestamp": event.timestamp,
                }
            )
        elif event.state == "timed_out":
            activity = get_activity()
            activity.update(
                {
                    "state": event.state,
                    "timeout_type": event.timeout_type,
                    "timeout_value": g_attr(
                        events[activity["scheduled_id"] - 1],
                        "{}_timeout".format(event.timeout_type.lower()),
                    ),
                    "timed_out_id": event.id,
                    "timed_out_timestamp": event.timestamp,
                }
            )
            if "retry" not in activity:
                activity["retry"] = 0
            else:
                activity["retry"] += 1
        elif event.state == "failed":
            activity = get_activity()
            activity.update(
                {
                    "state": event.state,
                    "reason": getattr(event, "reason", ""),
                    "details": getattr(event, "details", ""),
                    "failed_id": event.id,
                    "failed_timestamp": event.timestamp,
                }
            )
            if "retry" not in activity:
                activity["retry"] = 0
            else:
                activity["retry"] += 1
        elif event.state == "cancelled":
            activity = get_activity()
            activity.update(
                {
                    "state": event.state,
                    "details": getattr(event, "details", ""),
                    "cancelled_timestamp": event.timestamp,
                }
            )
        elif event.state == "cancel_requested":
            activity = {
                "type": "activity",
                "id": activity_id,
                "state": event.state,
                "cancel_requested_timestamp": event.timestamp,
                "cancel_decision_task_completed_event_id": event.decision_task_completed_event_id,
            }
            if activity_id not in self._activities:
                self._activities[activity_id] = activity
                self._tasks.append(activity)
            else:
                self._activities[activity_id].update(activity)

    def parse_child_workflow_event(
        self,
        events,  # type: List[Union[swf.models.event.Event, swf.models.event.ChildWorkflowExecutionEvent]]
        event,  # type: swf.models.event.ChildWorkflowExecutionEvent
    ):
        """Aggregate all the attributes of a workflow in a single entry.

        See https://docs.aws.amazon.com/amazonswf/latest/apireference/API_HistoryEvent.html

        - StartChildWorkflowExecutionInitiated: A request was made to start a
          child workflow execution.
        - StartChildWorkflowExecutionFailed: Failed to process
          StartChildWorkflowExecution decision. This happens when the decision
          is not configured properly, for example the workflow type specified
          is not registered.
        - ChildWorkflowExecutionStarted: A child workflow execution was
          successfully started.
        - ChildWorkflowExecutionCompleted: A child workflow execution, started
          by this workflow execution, completed successfully and was closed.
        - ChildWorkflowExecutionFailed: A child workflow execution, started by
          this workflow execution, failed to complete successfully and was
          closed.
        - ChildWorkflowExecutionTimedOut: A child workflow execution, started
          by this workflow execution, timed out and was closed.
        - ChildWorkflowExecutionCanceled: A child workflow execution, started
          by this workflow execution, was canceled and closed.
        - ChildWorkflowExecutionTerminated: A child workflow execution, started
          by this workflow execution, was terminated.
        """

        def get_workflow():
            initiated_event = events[event.initiated_event_id - 1]
            return self._child_workflows[initiated_event.workflow_id]

        if event.state == "start_initiated":
            workflow = {
                "type": "child_workflow",
                "id": event.workflow_id,
                "name": event.workflow_type["name"],
                "version": event.workflow_type["version"],
                "state": event.state,
                "initiated_event_id": event.id,
                "input": event.input,
                "child_policy": event.child_policy,
                "control": event.control,
                "tag_list": g_attr(event, "tag_list"),
                "task_list": event.task_list["name"],
                "initiated_event_timestamp": event.timestamp,
                "decision_task_completed_event_id": event.decision_task_completed_event_id,
            }
            if event.workflow_id not in self._child_workflows:
                self._child_workflows[event.workflow_id] = workflow
                self._tasks.append(workflow)
            else:
                # May have gotten a start_failed before (or retrying?)
                if (
                    self._child_workflows[event.workflow_id]["state"]
                    == "start_initiated"
                ):
                    # Should not happen anymore
                    logger.warning(
                        "start_initiated again for workflow {} (initiated @{}, we're @{})".format(
                            event.workflow_id,
                            self._child_workflows[event.workflow_id][
                                "initiated_event_id"
                            ],
                            event.id,
                        )
                    )
                self._child_workflows[event.workflow_id].update(workflow)
        elif event.state == "start_failed":
            workflow = {
                "state": event.state,
                "cause": event.cause,
                "control": event.control,
                "start_failed_id": event.id,
                "start_failed_timestamp": event.timestamp,
            }
            if event.workflow_id not in self._child_workflows:
                workflow.update(
                    {
                        "type": "child_workflow",
                        "id": event.workflow_id,
                        "name": event.workflow_type["name"],
                        "version": event.workflow_type["version"],
                        "decision_task_completed_event_id": event.decision_task_completed_event_id,
                    }
                )
                self._child_workflows[event.workflow_id] = workflow
                self._tasks.append(workflow)
            else:
                self._child_workflows[event.workflow_id].update(workflow)
        elif event.state == "started":
            workflow = get_workflow()
            workflow.update(
                {
                    "state": event.state,
                    "run_id": event.workflow_execution["runId"],
                    "workflow_id": event.workflow_execution["workflowId"],
                    "started_id": event.id,
                    "started_timestamp": event.timestamp,
                }
            )
        elif event.state == "completed":
            workflow = get_workflow()
            s = "result"
            workflow.update(
                {
                    "state": event.state,
                    "result": g_attr(event, s),
                    "completed_id": event.id,
                    "completed_timestamp": event.timestamp,
                }
            )
        elif event.state == "failed":
            workflow = get_workflow()
            workflow.update(
                {
                    "state": event.state,
                    "reason": g_attr(event, "reason"),
                    "details": g_attr(event, "details"),
                    "failed_id": event.id,
                    "failed_timestamp": event.timestamp,
                }
            )
            if "retry" not in workflow:
                workflow["retry"] = 0
            else:
                workflow["retry"] += 1
        elif event.state == "timed_out":
            workflow = get_workflow()
            workflow.update(
                {
                    "state": event.state,
                    "timeout_type": event.timeout_type,
                    "timeout_value": g_attr(
                        events[workflow["initiated_event_id"] - 1],
                        "{}_timeout".format(event.timeout_type.lower()),
                    ),
                    "timed_out_id": event.id,
                    "timed_out_timestamp": event.timestamp,
                }
            )
            if "retry" not in workflow:
                workflow["retry"] = 0
            else:
                workflow["retry"] += 1
        elif event.state == "canceled":
            workflow = get_workflow()
            workflow.update(
                {
                    "state": event.state,
                    "details": g_attr(event, "details"),
                    "canceled_id": event.id,
                    "canceled_timestamp": event.timestamp,
                }
            )
        elif event.state == "terminated":
            workflow = get_workflow()
            workflow.update(
                {
                    "state": event.state,
                    "terminated_id": event.id,
                    "terminated_timestamp": event.timestamp,
                }
            )

    def parse_workflow_event(
        self,
        _,
        event,  # type: swf.models.event.WorkflowExecutionEvent
    ):
        # type: (...) -> None
        """
        Parse a workflow event.
        """
        if event.state == "started":
            self.continued_execution_run_id = g_attr(
                event, "continued_execution_run_id"
            )
        elif event.state == "signaled":
            signal = {
                "type": "signal",
                "name": event.signal_name,
                "state": event.state,
                "external_initiated_event_id": g_attr(
                    event, "external_initiated_event_id"
                ),
                "external_run_id": getattr(
                    event, "external_workflow_execution", {}
                ).get("runId"),
                "external_workflow_id": getattr(
                    event, "external_workflow_execution", {}
                ).get("workflowId"),
                "input": event.input,
                "event_id": event.id,
                "timestamp": event.timestamp,
            }
            self._signals[event.signal_name] = signal
            self._tasks.append(signal)
        elif event.state == "cancel_requested":
            cancel_requested = {
                "type": event.state,
                "cause": g_attr(event, "cause"),
                "external_initiated_event_id": g_attr(
                    event, "external_initiated_event_id"
                ),
                "external_run_id": getattr(
                    event, "external_workflow_execution", {}
                ).get("runId"),
                "external_workflow_id": getattr(
                    event, "external_workflow_execution", {}
                ).get("workflowId"),
                "event_id": event.id,
                "timestamp": event.timestamp,
            }
            self._cancel_requested = cancel_requested
        elif event.state == "cancel_failed":
            cancel_failed = {
                "type": event.state,
                "cause": g_attr(event, "cause"),
                "event_id": event.id,
                "decision_task_completed_event_id": event.decision_task_completed_event_id,
                "timestamp": event.timestamp,
            }
            self._cancel_failed = cancel_failed

    def parse_external_workflow_event(
        self,
        events,  # type: List[Union[swf.models.event.Event, swf.models.event.ExternalWorkflowExecutionEvent]]
        event,  # type: swf.models.event.ExternalWorkflowExecutionEvent
    ):
        """
        Parse an external workflow event.
        """

        def get_workflow(workflows):
            initiated_event = events[event.initiated_event_id - 1]
            return workflows[initiated_event.workflow_id]

        if event.state == "signal_execution_initiated":
            workflow = {
                "type": "external_workflow",
                "id": event.workflow_id,
                "run_id": g_attr(event, "run_id"),
                "signal_name": event.signal_name,
                "state": event.state,
                "initiated_event_id": event.id,
                "input": event.input,
                "control": event.control,
                "initiated_event_timestamp": event.timestamp,
            }
            self._external_workflows_signaling[event.id] = workflow
        elif event.state == "signal_execution_failed":
            workflow = self._external_workflows_signaling[event.initiated_event_id]
            workflow.update(
                {
                    "state": event.state,
                    "cause": event.cause,
                    "signal_failed_timestamp": event.timestamp,
                }
            )
            if event.control:
                workflow["control"] = event.control
        elif event.state == "execution_signaled":
            workflow = self._external_workflows_signaling[event.initiated_event_id]
            workflow.update(
                {
                    "state": event.state,
                    "run_id": event.workflow_execution["runId"],
                    "workflow_id": event.workflow_execution["workflowId"],
                    "signaled_event_id": event.id,
                    "signaled_timestamp": event.timestamp,
                }
            )
            self._signaled_workflows[workflow["signal_name"]].append(workflow)
        elif event.state == "request_cancel_execution_initiated":
            workflow = {
                "type": "external_workflow",
                "id": event.workflow_id,
                "run_id": g_attr(event, "run_id"),
                "state": event.state,
                "control": event.control,
                "initiated_event_id": event.id,
                "initiated_event_timestamp": event.timestamp,
            }
            if event.workflow_id not in self._external_workflows_canceling:
                self._external_workflows_canceling[event.workflow_id] = workflow
            else:
                logger.warning(
                    "request_cancel_initiated again for workflow {} (initiated @{}, we're @{})".format(
                        event.workflow_id,
                        self._external_workflows_canceling[event.workflow_id][
                            "initiated_event_id"
                        ],
                        event.id,
                    )
                )
                self._external_workflows_canceling[event.workflow_id].update(workflow)
        elif event.state == "request_cancel_execution_failed":
            workflow = get_workflow(self._external_workflows_canceling)
            workflow.update(
                {
                    "state": event.state,
                    "cause": event.cause,
                    "request_cancel_failed_timestamp": event.timestamp,
                }
            )
            if event.control:
                workflow["control"] = event.control
        elif event.state == "execution_cancel_requested":
            workflow = get_workflow(self._external_workflows_canceling)
            workflow.update(
                {
                    "run_id": event.workflow_execution["runId"],
                    "workflow_id": event.workflow_execution["workflowId"],
                    "cancel_requested_event_id": event.id,
                    "cancel_requested_timestamp": event.timestamp,
                }
            )

    def parse_marker_event(
        self,
        _,
        event,  # type: swf.models.event.MarkerEvent
    ):
        # type: (...) -> None
        if event.state == "recorded":
            marker = {
                "type": "marker",
                "name": event.marker_name,
                "state": event.state,
                "details": g_attr(event, "details"),
                "event_id": event.id,
                "timestamp": event.timestamp,
            }
            self._markers.setdefault(event.marker_name, []).append(marker)
        elif event.state == "record_failed":
            marker = {
                "type": "marker",
                "name": event.marker_name,
                "state": event.state,
                "cause": event.cause,
                "record_failed_event_id": event.id,
                "record_failed_event_timestamp": event.timestamp,
            }
            self._markers.setdefault(event.marker_name, []).append(marker)

    def parse_timer_event(
        self,
        _,
        event,  # type: swf.models.event.TimerEvent
    ):
        # type: (...) -> None
        if event.state == "started":
            timer = {
                "type": "timer",
                "id": event.timer_id,
                "state": event.state,
                "start_to_fire_timeout": int(event.start_to_fire_timeout),
                "control": event.control,
                "started_event_id": event.id,
                "started_event_timestamp": event.timestamp,
                "decision_task_completed_event_id": event.decision_task_completed_event_id,
            }
            self._timers[event.timer_id] = timer
        elif event.state == "fired":
            timer = self._timers[event.timer_id]
            timer.update(
                {
                    "state": event.state,
                    "fired_event_id": event.id,
                    "fired_event_timestamp": event.timestamp,
                }
            )
        elif event.state == "start_failed":
            timer = self._timers.get(event.timer_id)
            if timer is None:
                timer = {
                    "type": "timer",
                    "id": event.timer_id,
                    "decision_task_completed_event_id": event.decision_task_completed_event_id,
                }
                self._timers[event.timer_id] = timer
            timer.update(
                {
                    "state": event.state,
                    "cause": event.cause,
                    "start_failed_event_id": event.id,
                    "start_failed_event_timestamp": event.timestamp,
                }
            )
        elif event.state == "canceled":
            timer = self._timers[event.timer_id]
            timer.update(
                {
                    "state": event.state,
                    "canceled_event_id": event.id,
                    "canceled_event_timestamp": event.timestamp,
                    "cancel_decision_task_completed_event_id": event.decision_task_completed_event_id,
                }
            )
        elif event.state == "cancel_failed":
            timer = self._timers.get(event.timer_id)
            if timer is None:
                timer = {
                    "type": "timer",
                    "id": event.timer_id,
                    "cancel_decision_task_completed_event_id": event.decision_task_completed_event_id,
                }
                self._timers[event.timer_id] = timer
            timer.update(
                {
                    "state": event.state,
                    "cause": event.cause,
                    "cancel_failed_event_id": event.id,
                    "cancel_failed_event_timestamp": event.timestamp,
                }
            )

    def parse_decision_event(
        self,
        _,
        event,  # type: swf.models.event.DecisionTaskEvent
    ):
        # type: (...) -> None
        if event.state == "started":
            self.started_decision_id = event.id
        elif event.state == "completed":
            self.completed_decision_id = event.id

    TYPE_TO_PARSER = {
        "ActivityTask": parse_activity_event,
        "DecisionTask": parse_decision_event,
        "ChildWorkflowExecution": parse_child_workflow_event,
        "WorkflowExecution": parse_workflow_event,
        "ExternalWorkflowExecution": parse_external_workflow_event,
        "Marker": parse_marker_event,
        "Timer": parse_timer_event,
    }

    def parse(self):
        """
        Parse the events.
        Update the corresponding statuses.
        """
        if not self._history:
            return

        events = self.events
        for event in events:
            parser = self.TYPE_TO_PARSER.get(event.type)
            if parser:
                parser(self, events, event)  # type: ignore

    @staticmethod
    def get_event_id(event):
        # type: (Dict[AnyStr, Any]) -> Optional[int]
        for event_id_key in (  # FIXME add a universal name?..
            "scheduled_id",
            "initiated_event_id",
            "event_id",
            "started_event_id",
            "cancel_failed_event_id",
        ):
            event_id = event.get(event_id_key)
            if event_id:
                return event_id
