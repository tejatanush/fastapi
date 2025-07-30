import pytest
from app.caluculations import add,subtract,multiply,divide,BankAccount

@pytest.fixture
def zero_bank_account():
    return BankAccount()

@pytest.fixture
def bank_account():
    return BankAccount(50)

@pytest.mark.parametrize("num1,num2,expected", [(3,2,5), (10,5,15), (0,0,0)])
def test_add(num1,num2,expected):
    sum=add(num1,num2)
    assert sum==expected

def tests_subtract():
    assert subtract(9,4)==5

def tests_multiply():
    assert multiply(9,4)==36

def tests_divide():
    assert divide(9,3)==3


def test_bank_set_initial_amount():
    bank_account=BankAccount(50)
    assert bank_account.balance==50

def test_bank_default_amount(zero_bank_account):
    assert zero_bank_account.balance==0

def test_withdraw():
    bank_account=BankAccount(30)
    bank_account.withdraw(20)
    assert bank_account.balance==10

def test_deposit():
    bank_account=BankAccount(50)
    bank_account.deposit(20)
    assert bank_account.balance==70
@pytest.mark.parametrize("deposited,withdrew,expected",
                        [(200,100,100), (50,10,40)])
def test_bank_transaction(zero_bank_account,deposited,withdrew,expected):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdrew)
    assert zero_bank_account.balance==expected