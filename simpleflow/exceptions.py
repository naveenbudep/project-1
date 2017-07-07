class ExecutionBlocked(Exception):
    pass


class TaskException(Exception):
    """
    Wrap an exception raised by a task.

    """
    def __init__(self, task, exception):
        """
        :param exception: raised by a task.
        :type  exception: TaskFailed.

        """
        self.task = task
        self.exception = exception

    def __repr__(self):
        return '{}(task={} exception={})'.format(
            self.__class__.__name__,
            self.task,
            self.exception)


class TaskFailed(Exception):
    """
    Wrap the error's *reason* and *details* for an task that failed.

    :param name: of the task that failed.
    :type name: str.
    :param reason: of the failure.
    :type  reason: str.
    :param details: of the failure.
    :type  details: str.

    """
    def __init__(self, name, reason, details=None):
        super(TaskFailed, self).__init__(name, reason, details)
        self.name = name
        self.reason = reason
        self.details = details

    def __repr__(self):
        return '{} ({}, "{}")'.format(
            self.__class__.__name__,
            self.name,
            self.reason,
        )


class TimeoutError(Exception):
    def __init__(self, timeout_type='unknown timeout', timeout_value=None):
        self.timeout_type = timeout_type
        self.timeout_value = timeout_value

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            self.timeout_type)


class TaskCanceled(Exception):
    def __init__(self, details=None):
        self.details = details


class TaskTerminated(Exception):
    pass


class AggregateException(Exception):
    """
    Class containing a list of exceptions.

    :type exceptions: list[Exception]
    """
    def __init__(self, exceptions):
        self.exceptions = exceptions

    def append(self, ex):
        self.exceptions.append(ex)

    def handle(self, handler, *args, **kwargs):
        """
        Invoke a user-defined handler on each exception.
        :param handler: Predicate accepting an exception and returning True if it's been handled.
        :type handler: (Exception) -> bool
        :param args: args for the handler
        :param kwargs: kwargs for the handler
        :raise: new AggregateException with the unhandled exceptions, if any
        """
        unhandled_exceptions = []
        for ex in self.exceptions:
            if ex and not handler(ex, *args, **kwargs):
                unhandled_exceptions.append(ex)
        if unhandled_exceptions:
            raise AggregateException(unhandled_exceptions)

    def flatten(self):
        """
        Flatten the AggregateException. Return a new instance without inner AggregateException.
        :return:
        :rtype: AggregateException
        """
        flattened_exceptions = []
        self._flatten(self, flattened_exceptions)
        return AggregateException(flattened_exceptions)

    @staticmethod
    def _flatten(exception, exceptions):
        if isinstance(exception, AggregateException):
            for ex in exception.exceptions:
                if ex:
                    AggregateException._flatten(ex, exceptions)
        else:
            exceptions.append(exception)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, repr([repr(ex) for ex in self.exceptions]))

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, str([str(ex) for ex in self.exceptions]))

    def __eq__(self, other):
        return self.exceptions == other.exceptions


class ExecutionError(Exception):
    pass
