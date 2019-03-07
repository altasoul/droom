
import datetime
import numbers
import random
import simpy
#import time


class Thing:
    pass

# Time utilities
def simdate(s):
    return datetime.date.fromisoformat(s).toordinal()

def isodate(x):
    return datetime.date.fromordinal(int(x)).isoformat()

def nextmonth(x):
    d = datetime.date.fromordinal(int(x))
    if d.month < 12:
        dnext = d.replace(month=d.month+1)
    else:
        dnext = d.replace(year=d.year+1, month=1)
    return dnext.toordinal()



class Scenario:
    def __init__(self, env):
        self.env = env

class Recurring_Bill:
    def __init__(self, env, name, start, amount, interval='monthly'):
        self.env = env
        self.name = name
        self.start = start
        if isinstance(amount, numbers.Number):
            self.lamount = lambda e: amount
        else:
            self.lamount = amount
        self.interval = interval
        self.action = env.process(self.run())

    def run(self):
        env = self.env
        yield env.timeout(self.start - env.now)
        while True:
            amt = self.lamount(env)
            print("{}: {} bill ${}".format(isodate(env.now), self.name, amt))
            yield self.env.timeout(nextmonth(env.now)-env.now)



def setup(env):
    rwb = Recurring_Bill(env, 'water', simdate('2019-04-15'), 123.45)
    reb = Recurring_Bill(env, 'electric', simdate('2019-04-15'),
                         lambda e: round(random.gauss(100, 30), 2))


def main():
    env = simpy.Environment(initial_time=simdate('2019-04-01'))
    setup(env)
    print(isodate(env.now))
    env.run(until=simdate('2021-01-01'))
    print(isodate(env.now))

if __name__ == '__main__':
    main()
