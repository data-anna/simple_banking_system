from random import randint


class SimpleBankingSystem:
    start_menu = f'1. Create an account \n2. Log into account \n0. Exit'
    login_menu = f'1. Balance\n2. Log out\n0. Exit'
    bank_iin = 400000  # Issuer Identification Number (IIN)

    def __init__(self):
        self.card_number = None
        self.card_PIN = None
        self.account_number = None
        self.current_balance = 0
        self.session_id = randint(100, 200)

    def show_start_menu(self):
        print(self.start_menu)
        menu_option = int(input())  # TODO: add non-int value handler
        if menu_option == 1:
            self.create_account()
            self.show_start_menu()
        elif menu_option == 2:
            self.log_in()
        elif menu_option == 0:
            print('\nBye!')
        else:
            print('\nPlease, choose one of the existing Menu options\n')
            self.show_start_menu()

    def create_account(self):
        self.generate_account_number()  # TODO: add check if account already created
        self.generate_card_pin()
        print(f'\nYour card has been created\nYour card number:\n{self.card_number}\nYour card PIN:\n{self.card_PIN}\n')

    def generate_account_number(self):
        self.account_number = self.int_concat(self.bank_iin, randint(100000000, 200000000))
        self.card_number = self.int_concat(self.account_number, self.return_checksum(self.account_number))
        return self.card_number

    def return_checksum(self, account_num):
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
        self.card_PIN = str(randint(0000, 9999)).zfill(4)
        return self.card_PIN

    def log_in(self):
        card = int(input('Enter your card number:\n'))
        PIN = input('Enter your PIN:\n')
        try:
            if self.card_number == card and self.card_PIN == PIN:
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
            self.show_current_balance()
            self.show_account_menu()
        elif account_option == 2:
            print('\nYou have successfully logged out!\n')
            self.show_start_menu()
        elif account_option == 0:
            print('\nBye!')
        else:
            print('\nPlease, choose one of the existing Login options\n')
            self.show_account_menu()

    def show_current_balance(self):
        print(f'\nBalance: {self.current_balance}\n')

    @staticmethod
    def int_concat(num1, num2):
        num1 = str(num1)
        num2 = str(num2)
        num1 += num2
        return int(num1)


SimpleBankingSystem().show_start_menu()
exit()
