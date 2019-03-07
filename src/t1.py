
import datetime
import numbers
import pdb
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

def next_month(x):
    d = datetime.date.fromordinal(int(x))
    if d.month < 12:
        dnext = d.replace(month=d.month+1)
    else:
        dnext = d.replace(year=d.year+1, month=1)
    return dnext.toordinal()

def next_week(x):
    return x + 7



class TimeUtil:
    def __init__(self, env):
        self.env = env

    def for_a_month(self):
        now = self.env.now
        return self.env.timeout(next_month(now)-now)

    def for_a_week(self):
        now = self.env.now
        return self.env.timeout(next_week(now)-now)


class Ledger:
    # very temporary placeholder
    def __init__(self):
        self.cash = 0

    def devit(self, amt):
        self.cash += amt        # To accountants Cash is a Debit account

    def credit(self, amt):
        self.cash -= amt

    def balance(self):
        return self.cash


class Scenario:
    def __init__(self, env, ledger):
        self.env = env
        self.ledger = ledger


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
        tu = TimeUtil(env)
        #yield env.timeout(self.start - env.now)
        t = env.timeout(self.start - env.now)
        print(repr(t.callbacks))
        t.callbacks.append(lambda e: print('callback from', e))
        while True:
            amt = self.lamount(env)
            print("{}: {} bill ${}".format(isodate(env.now), self.name, amt))
            #yield self.env.timeout(next_month(env.now)-env.now)
            if self.interval == 'monthly':
                yield tu.for_a_month()
            elif self.interval == 'weekly':
                yield tu.for_a_week()



def setup(env):
    rwb = Recurring_Bill(env, 'water', simdate('2019-04-15'), 123.45)
    reb = Recurring_Bill(env, 'electric', simdate('2019-04-10'),
                         lambda e: round(random.gauss(100, 30), 2))
    rgb = Recurring_Bill(env, 'groceries', simdate('2019-04-02'),
                         lambda e: round(random.gauss(60, 10), 2),
                         interval='weekly')


def main():
    env = simpy.Environment(initial_time=simdate('2019-04-01'))
    setup(env)
    print(isodate(env.now))
    env.run(until=simdate('2021-01-01'))
    print(isodate(env.now))

if __name__ == '__main__':
    main()
