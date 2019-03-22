import unittest

from t1 import Asset, Account, Ledger, NormalBalance, create_account
from t1 import JournalEntry

class TestAsset(unittest.TestCase):

    def setUp(self):
        pass

    def test_create(self):
        a1 = Asset(name='foo', value=42.31)
        self.assertEqual(a1.name, 'foo')
        self.assertEqual(a1.value, 42.31)

    def test_create_no_name(self):
        with self.assertRaises(TypeError):
            a1 = Asset(value=3)

    def test_create_no_value(self):
        with self.assertRaises(TypeError):
            a1 = Asset(name='foo')

    def test_create_extra_param(self):
        with self.assertRaises(TypeError):
            a1 = Asset(name='foo', value=42.31, convexity=0.3)

    def test_liquidate(self):
        a1 = Asset(name='foo', value=42.31)
        self.assertEqual(a1.liquidation_multiple, 0.8)
        self.assertEqual(a1.liquidation_value, 0.8 * 42.31)

    def test_liquidation_multiple(self):
        a1 = Asset(name='bar', value=12.34, liquidation_multiple=0.995)
        self.assertEqual(a1.liquidation_multiple, 0.995)
        self.assertEqual(a1.liquidation_value, 0.995 * 12.34)


class TestNormalBalance(unittest.TestCase):

    def test_init(self):
        cash = NormalBalance.DR
        retained_earnings = NormalBalance.CR

    def test_unique(self):
        self.assertNotEqual(NormalBalance.DR, NormalBalance.CR)

    def test_values(self):
        cash = NormalBalance.DR
        retained_earnings = NormalBalance.CR
        self.assertEqual(cash.name, 'DR')
        self.assertEqual(retained_earnings.name, 'CR')

    def test_is(self):
        cash = NormalBalance.DR
        retained_earnings = NormalBalance.CR
        self.assertIs(cash, NormalBalance.DR)
        self.assertIs(retained_earnings, NormalBalance.CR)


class TestAccount(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        a = Account('cash', NormalBalance.DR, balance=123.45)

    def test_repr(self):
        a = Account('cash', NormalBalance.DR, balance=123.45)
        self.assertEqual(repr(a), '<Account cash DR balance 123.45>')

    def test_value(self):
        a = Account('cash', NormalBalance.DR, balance=123.45)
        self.assertEqual(a.value, 123.45)
        a = Account('retained earnings', NormalBalance.CR, balance=123.45)
        self.assertEqual(a.balance, 123.45)
        self.assertEqual(a.value, -123.45)


class Test_create_account(unittest.TestCase):

    def test_repr(self):
        a = create_account('cash', NormalBalance.DR, balance=123.45)
        self.assertEqual(repr(a), '<Account cash DR balance 123.45>')
        a = create_account('cash')
        self.assertEqual(repr(a), '<Account cash DR balance 0>')

    def test_DR_CR(self):
        a = create_account('retained earnings', NormalBalance.CR, balance=123.45)
        self.assertEqual(a.balance, 123.45)
        self.assertEqual(a.value, -123.45)
        a = create_account('cash', balance=123.45)
        self.assertEqual(a.value, 123.45)
        a = Account('equity', 'CR', balance=123.45)
        self.assertEqual(a.balance, 123.45)
        self.assertEqual(a.value, -123.45)


class TestLedger(unittest.TestCase):

    def setUp(self):
        gl = Ledger()
        gl.add_account(create_account('cash'))
        gl.add_account(create_account('retained earnings', NormalBalance.CR, balance=123.45))
        gl.add_account(create_account('property taxes payable', 'CR', 51.23))
        self.gl = gl

    def test_init(self):
        gl = Ledger()

    def test_add_account(self):
        gl = Ledger()
        gl.add_account(create_account('cash'))
        gl.add_account(create_account('retained earnings', NormalBalance.CR, balance=123.45))
        gl.add_account(create_account('property taxes payable', 'CR', 51.23))

    def test_iter(self):
        self.assertEqual('|'.join(a.name for a in self.gl),
                         'cash|retained earnings|property taxes payable')

    def test_getitem(self):
        gl = self.gl
        self.assertEqual(gl['cash'].name, 'cash')
        self.assertEqual(gl['retained earnings'].balance, 123.45)
        self.assertEqual(gl['property taxes payable'].normal_balance.name, 'CR')


    def test_balance(self):
        gl = Ledger()
        gl.add_account(create_account('cash'))
        self.assertEqual(gl.balance, 0)
        gl.add_account(create_account('accounts payable', 'CR', 12.34))
        self.assertEqual(gl.balance, -12.34)
        gl.add_account(create_account('accounts receivable', balance=12.34))
        self.assertEqual(gl.balance, 0)
        gl.add_account(create_account('owners equity', NormalBalance.CR, balance=123.45))
        self.assertEqual(gl.balance, -123.45)
        gl.add_account(create_account('property taxes payable', 'CR', 51.23))
        self.assertEqual(gl.balance, -123.45 - 51.23)
        gl.add_account(create_account('retained earnings', 'CR', balance=12.34))
        self.assertEqual(gl.balance, -187.02)
        gl.add_account(create_account('inventory', balance=187.02))
        self.assertEqual(gl.balance, 0)


class TestJournalEntry(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        j = JournalEntry()

    def test_repr(self):
        j = JournalEntry(description="testing")
        self.assertEqual(repr(j), '<JournalEntry DR: [] CR:[] testing>')
        j.debit('inventory', 20)
        j.credit('cash', 5)
        j.credit('accounts payable', 15)
        self.assertEqual(repr(j),
		         r'''<JournalEntry DR: [('inventory', 20)] CR:[('cash', 5), ('accounts payable', 15)] testing>''')

    def test_balanced(self):
        j = JournalEntry()
        self.assertTrue(j.balanced)
        j.debit('inventory', 90)
        self.assertFalse(j.balanced)
        j.credit('cash', 10)
        self.assertFalse(j.balanced)
        j.credit('accounts payable', 80)
        self.assertTrue(j.balanced)
