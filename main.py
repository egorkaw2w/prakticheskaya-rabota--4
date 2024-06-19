import re
from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_info import abi, contract_adress

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
estate_agency_contract = w3.eth.contract(address=contract_adress, abi=abi)


account = None;
def authenticate_user():
    public_key_input = input("Введите адрес кошелька: ")
    pass_key = input("Укажите пароль: ")

    try:
        unlocked = w3.geth.personal.unlock_account(public_key_input, pass_key)
        if unlocked:
            print("Доступ в систему предоставлен.")
            return public_key_input
        else:
            print("Не удалось разблокировать аккаунт.")
            return None
    except Exception as authenticate_error:
        if 'already unlocked' in str(authenticate_error).lower():
            print("Аккаунт уже разблокирован.")
            return public_key_input
        else:
            print(f"Произошла ошибка во время авторизации: {authenticate_error}")
            return None

def register_new_user():
    while True:
        secure_password = input("Создайте пароль (не менее 12 символов, включающий цифры и спецсимволы): ")
        if is_password_secure(secure_password):
            verify_password = input("Подтвердите ваш пароль: ")
            if verify_password == secure_password:
                try:
                    new_account = w3.geth.personal.new_account(secure_password)
                    print(f"Регистрация прошла успешно. Ваш новый адрес: {new_account}")
                    break
                except Exception as e:
                    print(f"Произошла ошибка при регистрации: {e}")
            else:
                print("Пароли не совпадают. Пожалуйста, попробуйте снова.")
        else:
            print("Пароль слишком простой. Пароль должен содержать не менее 12 символов, включая цифры и спецсимволы.")

def ensure_account_unlocked():
    global account
    pass_key = input(f"Введите пароль для аккаунта {account}: ")
    try:
        unlocked = w3.geth.personal.unlock_account(account, pass_key)
        if unlocked:
            print("Аккаунт успешно разблокирован.")
        else:
            print("Не удалось разблокировать аккаунт.")
    except Exception as e:
        if 'already unlocked' in str(e).lower():
            print("Аккаунт уже разблокирован.")
        else:
            raise e

def add_property():
    global account;
    prop_size = int(input("Укажите размер недвижимости в квадратных метрах: "))
    prop_photo_url = input("Вставьте ссылку на фотографию недвижимости: ")
    prop_rooms = int(input("Укажите количество комнат: "))
    prop_type = int(input("Выберите тип объекта недвижимости (1 - Дом, 2 - Квартира, 3 - Лофт): ")) - 1

    try:
        estate_agency_contract.functions.createEstate(prop_size, prop_photo_url, prop_rooms, prop_type).transact({
            "from": account
        })
        print(f"Объект недвижимости был успешно добавлен.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def transaction_account_account():
    sender_account = input("Введите адрес аккаунта отправителя: ")
    ensure_account_unlocked(sender_account)
    
    receiver_account = input("Введите адрес аккаунта получателя: ")
    amount_in_ether = float(input("Введите сумму в Ether для перевода: "))
    amount_in_wei = w3.to_wei(amount_in_ether, 'ether')
    
    try:
        tx_hash = w3.eth.send_transaction({
            'from': sender_account,
            'to': receiver_account,
            'value': amount_in_wei
        })
        print(f"Перевод выполнен успешно. Хэш транзакции: {tx_hash.hex()}")
    except Exception as e:
        print(f"Произошла ошибка при переводе средств: {e}")

def add_advertisement():
    global account
    estates = estate_agency_contract.functions.getEstates().call()
    print("Доступная недвижимость:")
    for estate in estates:
        if estate[4] == account:
            print(f"ID: {estate[0]}, Тип: {estate[6]}, Активное: {'Да' if estate[3] else 'Нет'}")
    estate_id = int(input("Введите ID недвижимости для объявления: "))
    ad_price_in_ether = float(input("Установите цену для объявления в Ether: "))
    ad_price_in_wei = w3.to_wei(ad_price_in_ether, 'ether')
    
    try:
        estate_agency_contract.functions.createAd(estate_id, ad_price_in_wei).transact({
            "from": account
        })
        print(f"Объявление о продаже создано.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def add_balance():
    global account
    sum_in_ether = float(input("Сколько эфира вы хотите добавить на свой баланс? Укажите сумму в Ether: "))
    sum_in_wei = w3.to_wei(sum_in_ether, 'ether')
    
    try:
        tx_hash = estate_agency_contract.functions.addFunds().transact({
            'from': account,
            'value': sum_in_wei
        })
        print(f"Ваш баланс пополнен на {sum_in_ether} эфир. Хэш транзакции: {tx_hash.hex()}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def extract_funds():
    global account
    show_account_balance()
    balance = estate_agency_contract.functions.getBalance().call({
        "from": account
    })
    withdraw_amount_in_ether = float(input("Какую сумму в Ether вы желаете вывести? "))
    withdraw_amount_in_wei = w3.to_wei(withdraw_amount_in_ether, 'ether')
    
    if balance >= withdraw_amount_in_wei:
        try:
            withdraw_tx = estate_agency_contract.functions.withdraw().transact({
                "from": account
            })
            print(f"Средства в размере {withdraw_amount_in_ether} эфир выведены успешно. Транзакция: {withdraw_tx.hex()}")
        except Exception as e:
            print(f"Произошла ошибка при выводе средств: {e}")
    else:
        print("Недостаточно средств для вывода.")

def show_account_balance():
    global account
    try:
        balance = estate_agency_contract.functions.getBalance().call({
            "from": account
        })
        balance_in_ether = w3.from_wei(balance, 'ether')
        print(f"Текущий баланс: {balance_in_ether} эфир")
    except Exception as e:
        print(f"Произошла ошибка при получении баланса: {e}")

def alter_property_status():
    property_id = int(input("Введите ID недвижимости, чтобы изменить её статус: "))
    new_status = input("Введите новый статус (active/inactive): ").lower() == "active"
    
    try:
        estate_agency_contract.functions.updateEstateStatus(property_id, new_status).transact({
            "from": account
        })
        print(f"Статус недвижимости обновлён.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def alter_ad_status():
    global account
    ad_id = int(input("Введите ID объявления, чтобы изменить его статус: "))
    new_status = int(input("Введите новый статус (1 - Открыто, 2 - Закрыто): "))
    try:
        estate_agency_contract.functions.updateAdStatus(ad_id, new_status).transact({
            "from": account
        })
        print(f"Статус объявления обновлён.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def buy_property():
    global account
    ads = estate_agency_contract.functions.getAds().call()
    print("Доступные объявления:")
    for ad in ads:
        if ad[3]: 
            print(f"ID: {ads.index(ad)}, Цена: {w3.from_wei(ad[2], 'ether')} Ether, Владелец: {ad[0]}, Статус: {'Активное' if ad[5] == 0 else 'Закрыто'}")
    
    ad_id = int(input("Введите ID объявления для покупки: "))
    try:
        ad_price = ads[ad_id][2]
        balance = estate_agency_contract.functions.getBalance().call({
            "from": account
        })
        
        if balance >= ad_price:
            estate_agency_contract.functions.buyEstate(ad_id).transact({
                "from": account,
                "value": ad_price
            })
            print(f"Недвижимость успешно куплена.")
        else:
            print("Недостаточно средств для покупки")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def is_password_secure(password):
    if len(password) < 12:
        return False
    if re.search(r"\d", password) is None:
        return False
    if re.search(r"[A-Za-z]", password) is None:
        return False
    if re.search(r"[!@#$%^&*()\-_=+{};:,<.>\[\]]", password) is None:
        return False
    return True

def application_flow():
    global account
    user_account = None
    authenticated = False
    while True:
        try:
            if not authenticated:
                action = input("Выберите действие: \n1 - Вход\n2 - Регистрация\n")

                match action:
                    case "1":
                        user_account = authenticate_user()
                        account = user_account
                        authenticated = user_account is not None

                    case "2":
                        register_new_user()

            else:
                action = input("Выберите действие: \n1 - Пополнить баланс\n2 - Вывести средства\n3 - Проверить баланс\n4 - Добавить недвижимость\n5 - Добавить объявление\n6 - Изменить статус недвижимости\n7 - Купить недвижимость\n8 - Выйти\n")

                match action:
                    case "1":
                        add_balance()
                    case "2":
                        extract_funds()
                    case "3":
                        show_account_balance()
                    case "4":
                        add_property()
                    case "5":
                        add_advertisement()
                    case "6":
                        alter_property_status()
                    case "7":
                        buy_property()
                    case "8":
                        authenticated = False
                    case _:
                        print("Неизвестная команда.")
                        
        except Exception as general_error:
            print(f"Произошла ошибка: {general_error}")
            continue

if __name__ == '__main__':
    application_flow()