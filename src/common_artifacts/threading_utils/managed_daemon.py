# pylint: disable=unused-variable
#!/usr/bin/env python3

# ** info: python imports
from dataclasses import dataclass
from queue import PriorityQueue
from dataclasses import field
from datetime import datetime
from threading import Thread
from threading import Lock
import logging
import time
import uuid

# ** info: types imports
from typing import Callable
from typing import Union

# ** info: common artifacts imports
from src.common_artifacts.metaclass.singleton import Singleton

# pylint: disable=unused-variable
__all__: list[str] = [
    "large_process_thread_admin",
    "large_callable_task_queue",
    "LargeCallableTask",
]


@dataclass(order=True)
class ManagedDaemonTask:

    function: Callable = field(compare=False)
    kwargs: dict = field(compare=False)
    priority: int = field(compare=True, default=None)
    timestamp: Union[datetime, None] = field(compare=True, default=None)
    taskuuid: Union[str, None] = field(compare=False, default=None)

    def __post_init__(self):
        if self.taskuuid is None:
            self.taskuuid = uuid.uuid4()
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ManagedDaemonTaskQueue(metaclass=Singleton):
    def __init__(self) -> None:
        self.tasks_queue: PriorityQueue[ManagedDaemonTask] = PriorityQueue()
        self.lock: Lock = Lock()

    def add_task(self, task: ManagedDaemonTask) -> None:
        self.lock.acquire()
        self.tasks_queue.put_nowait(task)
        logging.info(f"adding task {task.taskuuid}")
        self.lock.release()
        return

    def get_task(self) -> ManagedDaemonTask:
        self.lock.acquire()
        self.tasks_queue.task_done()
        task: ManagedDaemonTask = self.tasks_queue.get_nowait()
        logging.info(f"getting task {task.taskuuid}")
        self.lock.release()
        return task

    def is_empty(self) -> bool:
        self.lock.acquire()
        is_empty: bool = self.tasks_queue.empty()
        self.lock.release()
        return is_empty

    def get_tasks_count(self) -> int:
        self.lock.acquire()
        unfinished_tasks: int = self.tasks_queue.unfinished_tasks
        self.lock.release()
        return unfinished_tasks


managed_daemon_task_queue: ManagedDaemonTaskQueue = ManagedDaemonTaskQueue()


class ManagedDaemon(metaclass=Singleton):
    def __init__(self) -> None:
        self.loading_thread: Thread = Thread(target=self.__managed_daemon__)
        self.loading_thread.daemon = True
        self.stop_event: bool = False
        self.lock: Lock = Lock()

    def start_managed_daemon(self) -> None:
        logging.info(r"starting large process thread")
        self.lock.acquire()
        self.stop_event = False
        self.lock.release()
        if self.loading_thread.is_alive() is False:
            self.loading_thread.start()
        else:
            self.loading_thread.run()
        return

    def end_managed_daemon(self) -> None:
        logging.info(r"joining large process thread")
        self.lock.acquire()
        self.stop_event = True
        self.lock.release()
        if self.loading_thread.is_alive() is True:
            self.loading_thread.join()
        return

    def __managed_daemon__(self) -> None:
        while True:

            self.lock.acquire()
            if self.stop_event is True:
                logging.info(r"stop event set true ending queue supervisor loop")
                break
            self.lock.release()

            logging.debug(f"tasks count: {managed_daemon_task_queue.get_tasks_count()}")
            logging.debug(f"is queue empty: {managed_daemon_task_queue.is_empty()}")

            if managed_daemon_task_queue.is_empty() is False:
                task: ManagedDaemonTask = managed_daemon_task_queue.get_task()
                logging.info(f"executiong task {task.taskuuid}")

                try:

                    task.function(**task.kwargs)

                # ! warning: super general exception handling here
                # pylint: disable=broad-except
                except Exception as exception:

                    logging.exception(
                        msg=f"error while executing task {task.taskuuid}: {exception.args[0]}"
                    )

            time.sleep(20)


managed_daemon: ManagedDaemon = ManagedDaemon()
