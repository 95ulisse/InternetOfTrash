import threading
import time as libtime

def synchronized_with_attr(lock_name):
    def decorator(method):
        def synced_method(self, *args, **kws):
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)
        return synced_method
    return decorator


class SyncOrderedList:

    def __init__(self):
        self.syncList = []
        self.lock = threading.RLock()


    @synchronized_with_attr("lock")
    def is_in(self, arduino_id):
        for i in range(len(self.syncList)):
            if arduino_id == self.syncList[i][0]:
                return i

        return -1

    @synchronized_with_attr("lock")
    def print_list(self):
        print("\n-------CURRENT TASKS-------")
        print("---------------------------")
        for i, el in enumerate(self.syncList):
            realtime = max(0, int(el[1]-libtime.time()))
            print(i, " | ID: ", el[0], " | Time: ", realtime , " | Force: " , el[2], " | ReqID: ", el[3])

        print("---------------------------\n")

    @synchronized_with_attr("lock")
    def put(self, bin_id, msg={'reqId':-1}, time=0, force=False):
        idx = self.is_in(bin_id)
        if idx > -1:
            self.remove_element(idx)
        for i in range(len(self.syncList)):
                if libtime.time()+time <= self.syncList[i][1]:
                        self.syncList.insert(i, (bin_id, libtime.time()+time, force, msg['reqId']))
                        self.print_list()
                        return
        self.syncList.append((bin_id, libtime.time()+time, force, msg['reqId']))
        self.print_list()

    @synchronized_with_attr("lock")
    def remove_element(self, index):
        del(self.syncList[index])


    @synchronized_with_attr("lock")
    def get_first(self):
        if len(self.syncList) == 0:
            raise ValueError("Empty list")
        return self.syncList[0]

    @synchronized_with_attr("lock")
    def wait_for_task(self):
        if self.empty():
            return libtime.time()+5
        else:
            return int(self.get_first()[1])

    @synchronized_with_attr("lock")
    def pop(self):
        if len(self.syncList) == 0:
            raise ValueError("Empty list")

        first = self.syncList[0]
        self.syncList = self.syncList[1:]
        return first


    @synchronized_with_attr("lock")
    def empty(self):
        return len(self.syncList) == 0

