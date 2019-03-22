
import datetime
import enum
import numbers
import pdb
import random
import simpy
import typing
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


class NormalBalance(enum.Enum):
    DR = enum.auto()
    CR = enum.auto()
    

class Account:
    def __init__(self, name: str, normal_balance = 'DR',
                 balance: float = 0.0, description: str = None):
        self.name: str = name
        if normal_balance == 'DR':
            self.normal_balance = NormalBalance.DR
        elif normal_balance == 'CR':
            self.normal_balance = NormalBalance.CR
        else:
            self.normal_balance = normal_balance
        self.balance: float = balance
        self.description = description

    def __repr__(self) -> str:
        return f'<Account {self.name} {self.normal_balance.name} balance {self.balance}>'

    @property
    def value(self) -> float:
        if self.normal_balance is NormalBalance.DR:
            rv = self.balance
        else:
            rv = -self.balance
        return rv

    def debit(self, amount: float) -> None:
        if self.normal_balance is NormalBalance.DR:
            self.balance += amount
        else:
            self.balance -= amount

    def credit(self, amount: float) -> None:
        if self.normal_balance is NormalBalance.CR:
            self.balance += amount
        else:
            self.balance -= amount


def create_account(name, nb='DR', balance=0, description=''):
    if nb == 'DR':
        normal_balance = NormalBalance.DR
    elif nb == 'CR':
        normal_balance = NormalBalance.CR
    else:
        normal_balance = nb
    return Account(name, normal_balance, balance, description)


class Ledger:
    def __init__(self):
        self.acct_dict = dict()
        
    def add_account(self, account):
        self.acct_dict[account.name] = account

    def __iter__(self):
        return iter(self.acct_dict.values())

    def __getitem__(self, account_name):
        return self.acct_dict[account_name]

    @property
    def balance(self):
        return sum(account.value for account in self)

    def post(self, journal_entry):
        if not isinstance(journal_entry, JournalEntry):
            raise TypeError('JournalEntry expected')
        if not journal_entry.balanced:
            raise(ValueError, 'journal entry not balanced')
        for account_name, amount in journal_entry.dr:
            self[account_name].debit(amount)
        for account_name, amount in journal_entry.cr:
            self[account_name].credit(amount)


class JournalEntry:
    def __init__(self, description = None, dr = None,  cr = None):
        self.description = description
        self.dr = dr or []
        self.cr = cr or []

    def __repr__(self) -> str:
        return f'<JournalEntry DR: {self.dr} CR:{self.cr} {self.description}>'

    def debit(self, account, amount):
        self.dr.append((account, amount))

    def credit(self, account, amount):
        self.cr.append((account, amount))

    @property
    def balanced(self):
        return sum(amt for (acct, amt) in self.dr) == sum(amt for (acct, amt) in self.cr)


class Asset:
    def __init__(self, name: str, value: float, description=None,
                 liquidation_multiple:float = 0.8):
        self.name = name
        self.value = value
        self.description = description or ''
        self.liquidation_multiple = liquidation_multiple

    @property
    def liquidation_value(self) -> float:
        return self.value * self.liquidation_multiple

    def __repr__(self) -> str:
        return f'<Asset {self.name} value {self.value}>'



class AssetPool:
    pass



class Investor:
    # Assets, Liabilities, strategy
    def __init__(self, config):
        self.config = config
        self.accounts = Ledger()

    def raise_cash(self, amt):
        # https://www.accountingtools.com/articles/2017/5/17/debits-and-credits
        pass


# A financial can be run through

class NameMe:
    # The rules and initial conditions
    def __init__(self, env):
        self.env = env
        self.bills = []


class Scenario:
    # Initial conditions, exogenous events, random outside forces
    def __init__(self, env, ledger):
        self.env = env
        self.ledger = ledger


class Trial:  # or function in Scenario
    # Run an Investor in a Scenario to obtain a Trajectory
    def __init__(self, env):
        self.env = env
        self.bills = []


class Trajectory:
    # A particular path thru phase spece as the result of a Trial
    pass




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
