import threading
import time


class Worker(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name            # thread 이름 지정

    def run(self):
        print("sub thread start ", threading.currentThread().getName())
        time.sleep(5)
        print("sub thread end ", threading.currentThread().getName())


print("main thread start")

t1 = Worker("1")        # sub thread 생성
t1.start()              # sub thread의 run 메서드를 호출

t2 = Worker("2")        # sub thread 생성
t2.start()              # sub thread의 run 메서드를 호출

t1.join()
t2.join()

print("main thread post job")
print("main thread end")