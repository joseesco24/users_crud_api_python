# Commons
from src.commons.singleton import Singleton
from dataclasses import dataclass
from queue import PriorityQueue
from dataclasses import field
from threading import Thread
from threading import Lock
import traceback
import threading
import logging
import time
import uuid


__all__ = ["ThreadPoolQueueTask", "thread_pool_queue", "start_queue_listener"]


@dataclass(order=True)
class ThreadPoolQueueTask:
    function: callable = field(compare=False)
    kwargs: dict = field(compare=False)
    priority: int

    __taskuuid__: str = field(compare=False, default=None)

    def __post_init__(self):
        if self.__taskuuid__ is None:
            self.__taskuuid__ = uuid.uuid4()


class ThreadPoolQueue(metaclass=Singleton):
    def __init__(self, tasksQueueMaxSize: int = 400):
        self.tasksQueue: PriorityQueue[ThreadPoolQueueTask] = PriorityQueue(
            maxsize=tasksQueueMaxSize
        )
        self.lock: Lock = Lock()

    def addTask(self, task: ThreadPoolQueueTask) -> None:
        logging.info(
            f"adding task to thread pool priority queue on:{threading.currentThread().ident} - unfinished tasks:{self.tasksQueue.unfinished_tasks} queue max size:{self.tasksQueue.maxsize}"
        )
        logging.info(
            f"task meta - task name:{task.function.__name__} - task kwargs:{task.kwargs} - task priority:{task.priority} - task id:{task.__taskuuid__}"
        )
        self.lock.acquire()
        self.tasksQueue.put_nowait(task)
        self.lock.release()
        return

    def getNextTask(self) -> ThreadPoolQueueTask:
        logging.info(
            f"executing task from thread pool priority queue on:{threading.currentThread().ident} - unfinished tasks:{self.tasksQueue.unfinished_tasks} queue max size:{self.tasksQueue.maxsize}"
        )

        self.lock.acquire()
        self.tasksQueue.task_done()
        task: ThreadPoolQueueTask = self.tasksQueue.get_nowait()
        self.lock.release()

        logging.info(
            f"task meta - task name:{task.function.__name__} - task kwargs:{task.kwargs} - task priority:{task.priority} - task id:{task.__taskuuid__}"
        )

        return task

    def isEmpty(self) -> bool:
        self.lock.acquire()
        is_empty: bool = self.tasksQueue.empty()
        self.lock.release()
        return is_empty

    def getUnfinishedTasksCount(self) -> int:
        self.lock.acquire()
        unfinished_tasks: int = self.tasksQueue.unfinished_tasks
        self.lock.release()
        return unfinished_tasks


thread_pool_queue: ThreadPoolQueue = ThreadPoolQueue()


class ThreadPoolAdmin(metaclass=Singleton):
    def __init__(self):
        self.loadingThread: Thread = Thread(target=self.__thread_pool_admin__)
        self.loadingThread.daemon = True
        self.lock: Lock = Lock()

    def start_thread_pool_admin(self) -> None:
        logging.info(f"running thread admin on {self.loadingThread.ident}")
        if self.loadingThread.is_alive() is False:
            self.loadingThread.start()
        else:
            self.loadingThread.run()
        return

    def end_thread_pool_admin(self) -> None:
        logging.info(f"joining thread admin on {self.loadingThread.ident}")
        if self.loadingThread.is_alive() is True:
            self.loadingThread.join()
        return

    def __thread_pool_admin__(self):
        while True:

            logging.debug(
                f"thread admin on:{self.loadingThread.ident} - unfinished tasks:{thread_pool_queue.getUnfinishedTasksCount()} - queue status:{thread_pool_queue.isEmpty()}"
            )

            current_task: ThreadPoolQueueTask

            try:

                if thread_pool_queue.isEmpty() is False:
                    task: ThreadPoolQueueTask = thread_pool_queue.getNextTask()
                    current_task = task
                    logging.info(
                        f"executiong task {task.__taskuuid__} on thread:{self.loadingThread.ident}"
                    )
                    logging.info(
                        f"task meta - task name:{task.function.__name__} - task kwargs:{task.kwargs} - task priority:{task.priority} - task id:{task.__taskuuid__}"
                    )
                    task.function(**task.kwargs)

            except Exception as exception:
                logging.error(
                    f"error while executing task - task id:{current_task.__taskuuid__} - error message{exception} - \n\nerror traceback:\n\n{traceback.format_exc(chain=False)}"
                )
                logging.info(
                    f"task meta - task name:{current_task.function.__name__} - task kwargs:{current_task.kwargs} - task priority:{current_task.priority} - task id:{current_task.__taskuuid__}"
                )

            time.sleep(10)


thread_pool_admin: ThreadPoolAdmin = ThreadPoolAdmin()
