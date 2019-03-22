import unittest

from t1 import Asset, Account, Ledger, NormalBalance, create_account


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
        pass

    def test_init(self):
        gl = Ledger()

    def x_test_create_account(self):
        gl = Ledger()
        gl.create_account('cash')
        gl.create_account('retained earnings', NormalBalance.CR, balance=123.45)
        gl.create_account('property taxes payable', 'CR', 51.23)

    def test_add_account(self):
        gl = Ledger()
        gl.add_account(create_account('cash'))
        gl.add_account(create_account('retained earnings', NormalBalance.CR, balance=123.45))
        gl.add_account(create_account('property taxes payable', 'CR', 51.23))

    def test_iter(self):
        gl = Ledger()
        gl.add_account(create_account('cash'))
        gl.add_account(create_account('retained earnings', NormalBalance.CR, balance=123.45))
        gl.add_account(create_account('property taxes payable', 'CR', 51.23))
        self.assertEqual('|'.join(a.name for a in gl),
                         'cash|retained earnings|property taxes payable')

    def test_balance(self):
        gl = Ledger()
        gl.add_account(create_account('cash'))
        self.assertEqual(gl.balance, 0)
        gl.add_account(create_account('accounts payable', 'CR', 12.34))
        self.assertEqual(gl.balance, -12.34)
        gl.add_account(create_account('accounts receivable', balance=12.34))
        self.assertEqual(gl.balance, 0)
        return

        gl.add_account(create_account('owners equity', NormalBalance.CR, balance=123.45))
        self.assertEqual(gl.balance, -123.45)
        gl.add_account(create_account('property taxes payable', 'CR', 51.23))
        self.assertEqual(gl.balance, -123.45 - 51.23)
        gl.add_account(create_account('retained earnings', 'CR', balance=12.34))
        self.assertEqual(gl.balance, -187.02)
        gl.add_account(create_account('inventory', balance=174.68))
        self.assertEqual(gl.balance, 0)
