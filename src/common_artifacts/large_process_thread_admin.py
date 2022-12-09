#!/usr/bin/env python3

# ** info: python imports
from dataclasses import dataclass
from queue import PriorityQueue
from dataclasses import field
from threading import Thread
from threading import Lock
import logging
import time
import uuid

# ** info: common artifacts imports
from src.common_artifacts.singleton import Singleton


__all__ = [
    "large_process_thread_admin",
    "large_callable_task_queue",
    "LargeCallableTask",
]


@dataclass(order=True)
class LargeCallableTask:
    function: callable = field(compare=False)
    kwargs: dict = field(compare=False)
    priority: int

    __taskuuid__: str = field(compare=False, default=None)

    def __post_init__(self):
        if self.__taskuuid__ is None:
            self.__taskuuid__ = uuid.uuid4()


class LargeCallableTaskQueue(metaclass=Singleton):
    def __init__(self):
        self.tasksQueue: PriorityQueue[LargeCallableTask] = PriorityQueue()
        self.lock: Lock = Lock()

    def addTask(self, task: LargeCallableTask) -> None:
        self.lock.acquire()
        self.tasksQueue.put_nowait(task)
        logging.info(
            f"adding task {task.__taskuuid__}", extra={"taskMetadata": {**task}}
        )
        self.lock.release()
        return

    def getTask(self) -> LargeCallableTask:
        self.lock.acquire()
        self.tasksQueue.task_done()
        task: LargeCallableTask = self.tasksQueue.get_nowait()
        logging.info(
            f"getting task {task.__taskuuid__}", extra={"taskMetadata": {**task}}
        )
        self.lock.release()
        return task

    def isEmpty(self) -> bool:
        self.lock.acquire()
        is_empty: bool = self.tasksQueue.empty()
        self.lock.release()
        return is_empty

    def getTasksCount(self) -> int:
        self.lock.acquire()
        unfinished_tasks: int = self.tasksQueue.unfinished_tasks
        self.lock.release()
        return unfinished_tasks


large_callable_task_queue: LargeCallableTaskQueue = LargeCallableTaskQueue()


class LargeProcessThreadAdmin(metaclass=Singleton):
    def __init__(self) -> None:
        self.loadingThread: Thread = Thread(target=self.__large_process_thread_admin__)
        self.loadingThread.daemon = True
        self.stop_event: bool = False
        self.lock: Lock = Lock()

    def start_large_process_thread_admin(self) -> None:
        logging.info(f"starting large process thread")
        self.lock.acquire()
        self.stop_event = False
        self.lock.release()
        if self.loadingThread.is_alive() is False:
            self.loadingThread.start()
        else:
            self.loadingThread.run()
        return

    def end_large_process_thread_admin(self) -> None:
        logging.info(f"joining large process thread")
        self.lock.acquire()
        self.stop_event = True
        self.lock.release()
        if self.loadingThread.is_alive() is True:
            self.loadingThread.join()
        return

    def __large_process_thread_admin__(self) -> None:
        while True:

            self.lock.acquire()
            if self.stop_event is True:
                logging.info(r"stop event set true ending queue supervisor loop")
                break
            self.lock.release()

            logging.debug(f"tasks count: {large_callable_task_queue.getTasksCount()}")
            logging.debug(f"is queue empty: {large_callable_task_queue.isEmpty()}")

            if large_callable_task_queue.isEmpty() is False:
                task: LargeCallableTask = large_callable_task_queue.getTask()
                logging.info(f"executiong task {task.__taskuuid__}")

                try:
                    task.function(**task.kwargs)
                except Exception as exception:
                    logging.exception(
                        msg=f"error while executing task {task.__taskuuid__}: {exception.args[0]}"
                    )

            time.sleep(20)


large_process_thread_admin: LargeProcessThreadAdmin = LargeProcessThreadAdmin()
