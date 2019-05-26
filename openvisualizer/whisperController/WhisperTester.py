import threading, time

class RotatingQueue:

    def __init__(self):
        self.queue = []
        self.count = 0

    def add(self, item):
        self.queue.append(item)

    def get(self):
        item = self.queue[self.count]
        self.count = (self.count + 1) % len(self.queue)
        return item



class WhisperTester(threading.Thread):

    def __init__(self, controller):
        super(WhisperTester, self).__init__()
        self.command = RotatingQueue()
        self.command.add("dio 655 f7f 512 root".split(' '))
        self.command.add("dio 655 f07 5000 root".split(' '))
        self.command.add("dio 655 f7f 5000 root".split(' '))
        self.interval = 30 # 30 seconds
        self.times = 180 # perform command 5 times
        self.controller = controller

    def setCommand(self, command):
        self.command = command

    def setInterval(self, interval):
        self.interval = interval

    def setTimes(self, times):
        self.times = times

    def run(self):
        for i in range(self.times):
            command = self.command.get()
            print(command)
            self.controller.parse(command, "/dev/ttyUSB1")
            time.sleep(self.interval)
