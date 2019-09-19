

def main():
    print("python main function")

# class Person:
#   def __init__(self, name, age):
#     self.name = name
#     self.age = age
#
# p1 = Person("John", 36)
#
# print(p1.name)
# print(p1.age)
import signal
import time


def alarm_handler(signum, stack):
    print('Alarm at:', time.ctime())


signal.signal(signal.SIGALRM, alarm_handler)  # assign alarm_handler to SIGALARM
signal.alarm(4)  # set alarm after 4 seconds
print('Current time:', time.ctime())
time.sleep(6)  # make sufficient delay for the alarm to happen