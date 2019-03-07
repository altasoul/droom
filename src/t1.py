
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


# A financial can be run through

class NameMe:
    # The rules and initial conditions
    def __init__(self, env):
        self.env = env
        self.bills = []


class Scenario:
    # exogenous events
    def __init__(self, env, ledger):
        self.env = env
        self.ledger = ledger


def recurring_event(env, start, interval='monthly'):
    tu = TimeUtil(env)
    if interval == 'monthly':
        waiter = tu.for_a_month
    elif interval == 'weekly':
        waiter = tu.for_a_week
    else:
        raise(ValueError, 'unrecognized interval')
    yield env.timeout(start - env.now)
    while True:
        yield waiter()


def recurring_bill(env, start, name, amount, interval='monthly'):
    if isinstance(amount, numbers.Number):
        amount_fun = lambda e: amount
    else:
        amount_fun = amount
    for e in recurring_event(env, start, interval):
        yield e
        print("{}: {} bill ${}".format(isodate(env.now), name,
                                       amount_fun(env)))

def setup(env):
    rwb = recurring_bill(env, simdate('2019-04-15'), 'water', 123.45)
    env.process(rwb)
    reb = recurring_bill(env, simdate('2019-04-10'), 'electric',
                         lambda e: round(random.gauss(100, 30), 2))
    env.process(reb)
    rgb = recurring_bill(env, simdate('2019-04-02'), 'groceries',
                         lambda e: round(random.gauss(60, 10), 2),
                         interval='weekly')
    env.process(rgb)


def main():
    env = simpy.Environment(initial_time=simdate('2019-04-01'))
    setup(env)
    print(isodate(env.now))
    env.run(until=simdate('2021-01-01'))
    print(isodate(env.now))

if __name__ == '__main__':
    random.seed(0)
    main()
