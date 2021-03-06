from random import randint
import sqlite3


class BankingDatabase:
    db_file = '../card.s3db'
    sql_create_card_table = """CREATE TABLE IF NOT EXISTS card (
                        id INTEGER PRIMARY KEY AUTOINCREMENT
                        , number TEXT NOT NULL
                        , pin TEXT
                        , balance INTEGER DEFAULT 0
                                    );"""

    def __init__(self):
        self.db_conn = None
        self.cur = None
        self.db_init()
        self.db_create_tables()

    def db_init(self):
        try:
            self.db_conn = sqlite3.connect(self.db_file)
            self.cur = self.db_conn.cursor()
        except sqlite3.Error as e:
            print(e)

    def db_create_tables(self):
        """ This method includes all the tables that should be created in card.s3db
        """
        self.create_table(self.db_conn, self.sql_create_card_table)

    @staticmethod
    def create_table(db_conn, create_table_sql):
        try:
            c = db_conn.cursor()
            c.execute(create_table_sql)
            db_conn.commit()
        except sqlite3.Error as e:
            print(e)

    def db_insert_account_num(self, acc_num, pin):
        try:
            with self.db_conn:
                self.cur.execute("INSERT INTO card(number, pin) VALUES (:number, :pin)",
                                 {'number': acc_num, 'pin': pin})
        except sqlite3.IntegrityError as e:
            print(e)

    def db_get_card_pin(self, card_num):
        with self.db_conn:
            self.cur.execute("SELECT pin FROM card WHERE number=:number", {'number': card_num})
            return self.cur.fetchone()

    def db_get_card_balance(self, card_num):
        with self.db_conn:
            self.cur.execute("SELECT balance FROM card WHERE number=:number", {'number': card_num})
            return self.cur.fetchone()

    def db_add_income_to_balance(self, card, income):
        with self.db_conn:
            self.cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?", (income, card))

    def db_remove_account(self, card_number):
        with self.db_conn:
            self.cur.execute("DELETE FROM card WHERE number = ?", (card_number,))


class CustomerInfo:
    # POJO
    def __init__(self):
        self.account_number = None
        self.card_number = None
        self.card_pin = None
        self.current_balance = 0


class BankingConsoleInterface:
    start_menu = f'1. Create an account \n2. Log into account \n0. Exit'
    login_menu = f'1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit'
    bank_iin = 400000  # Issuer Identification Number (IIN)

    def __init__(self):
        self.db = BankingDatabase()
        self.customer = CustomerInfo()
        self.show_start_menu()

    def show_start_menu(self):
        print(self.start_menu)
        try:
            global menu_option
            menu_option = int(input())
        except ValueError:
            print('\nPlease, choose one of the existing Menu options\n')
            self.show_start_menu()

        if menu_option == 1:
            self.db.db_insert_account_num(self.generate_account_number(), self.generate_card_pin())
            print(
                f'\nYour card has been created\nYour card number:\n{self.customer.card_number}\nYour card PIN:\n{self.customer.card_pin}\n')
            self.show_start_menu()
        elif menu_option == 2:
            self.log_in()
        elif menu_option == 0:
            self.db.cur.close()
            self.db.db_conn.close()
            print('\nBye!')
        else:
            print('\nPlease, choose one of the existing Menu options\n')
            self.show_start_menu()

    def generate_account_number(self):
        # TODO: move simple generators to class BankingUtils
        self.customer.account_number = self.concatenate_integers(self.bank_iin, randint(100000000, 200000000))
        self.customer.card_number = self.concatenate_integers(self.customer.account_number,
                                                              self.return_checksum(self.customer.account_number))
        return self.customer.card_number

    @staticmethod
    def concatenate_integers(num1, num2):
        num1 = str(num1)
        num2 = str(num2)
        num1 += num2
        return int(num1)

    @staticmethod
    def return_checksum(account_num):
        counter = 0
        for i, value in enumerate(list(str(account_num)), start=1):
            if i % 2 == 0:
                counter += int(value)
            elif int(value) * 2 > 9:
                counter += (int(value) * 2) - 9
            else:
                counter += (int(value) * 2)
        return 10 - (counter % 10) if (counter % 10) > 0 else 0

    def generate_card_pin(self):
        self.customer.card_pin = str(randint(0000, 9999)).zfill(4)
        return self.customer.card_pin

    def log_in(self):
        self.customer.card_number = input('Enter your card number:\n').strip()
        self.customer.card_pin = input('Enter your PIN:\n').strip()
        try:
            if self.db.db_get_card_pin(self.customer.card_number) is None:
                print('\nWrong card number or PIN!\n')
                self.show_start_menu()
            elif self.db.db_get_card_pin(self.customer.card_number)[0] == self.customer.card_pin:
                print('\nYou have successfully logged in!\n')
                self.show_account_menu()
            else:
                print('\nWrong card number or PIN!\n')
                self.show_start_menu()
        except KeyError:
            print('\nWrong card number or PIN!\n')

    def show_account_menu(self):
        print(self.login_menu)
        account_option = int(input())
        if account_option == 1:
            print(f'\nBalance: {self.db.db_get_card_balance(self.customer.card_number)[0]}\n')
            self.show_account_menu()
        elif account_option == 2:
            income = int(input('Enter income:\n').strip())
            self.db.db_add_income_to_balance(self.customer.card_number, income)
            print('\nIncome was added!\n')
            self.show_account_menu()
        elif account_option == 3:
            self.transfer_amount()
        elif account_option == 4:
            self.db.db_remove_account(self.customer.card_number)
            print('\nThe account has been closed!\n')
            self.show_start_menu()
        elif account_option == 5:
            print('\nYou have successfully logged out!\n')
            self.show_start_menu()
        elif account_option == 0:
            self.db.cur.close()
            self.db.db_conn.close()
            print('\nBye!')
        else:
            print('\nPlease, choose one of the existing Login options\n')
            self.show_account_menu()

    def transfer_amount(self):
        transfer_card = input('Transfer\nEnter card number:\n').strip()
        if self.customer.card_number == transfer_card:
            print("\nYou can't transfer money to the same account!\n")
            self.show_account_menu()
        elif transfer_card[-1] != str(self.return_checksum(transfer_card[:-1])):
            print('\nProbably you made a mistake in the card number. Please try again!\n')
            self.show_account_menu()
        elif self.db.db_get_card_balance(transfer_card) is None:
            print('\nSuch a card does not exist.\n')
            self.show_account_menu()
        else:
            transfer_amount = int(input('Enter how much money you want to transfer:\n').strip())
            if transfer_amount > self.db.db_get_card_balance(self.customer.card_number)[0]:
                print('Not enough money!\n')
                self.show_account_menu()
            else:
                # TODO: make transactional on a DB level (ex. open transaction, commit)
                self.db.db_add_income_to_balance(self.customer.card_number, -transfer_amount)
                self.db.db_add_income_to_balance(transfer_card, transfer_amount)
                print('Success!\n')
                self.show_account_menu()


if __name__ == '__main__':
    BankingConsoleInterface()
exit()
