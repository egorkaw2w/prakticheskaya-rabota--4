import re
from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_info import abi, contract_adress

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(address=contract_adress, abi=abi)
accounts = w3.eth.accounts

login = None

def errors(e):
    if "У вас недостаточно средств" in str(e):
        print("У вас недостаточно средств")
    elif "Вы не владелец недвижимоси" in str(e):
        print("Вы не владелец недвижимости")
    elif "Недвижимость недоступна" in str(e):
        print("Недвижимость недоступна")
    elif "Данное объявление закрыто" in str(e):
        print("Данное объявление закрыто")
    elif "Владелец не может купить свою недвижимость" in str(e):
        print("Владелец не может купить свою недвижимость")
    else:
        print("Произошла неизвестная ошибка")

def menu():
    print("Выберите действие: ")
    print("1.Создать недвижимости")
    print("2.Создать объявление")
    print("3.Изменение недвижемости")
    print("4.Изменение объявление")
    print("5.Купить недвижимость")
    print("6.Посмотреть все объявления")
    print("7.Посмотреть все недвижимости")
    print("8.Посмотреть баланс")
    print("9.Выйти")
    choice = input()
    match choice:
        case "1":
            createEs()
        case "2":
            createAd()
        case"3":
            changeEs()
        case "4":
            changeAd()
        case "5":
            buy()
        case"6":
            getAllAds()
        case "7":
            getAllEs()
        case"8":
            getBalance()
        case "9":
             main()
        case _:
            print("Некорректный ввод")
    menu()

def createEs():
    global login
    size = input("Введите размер недвижимости: ")
    picture = input("Введите фото недвижимости: ")
    rooms = input("Введите кол-во комнат недвижимости: ")
    type = input("Введите тип недвижимости: ")
    try:
        contract.functions.createEstate(int(size), str(picture), int(rooms), int(type)).transact({'from': login})
        print("Недвижимость успешно создана")
        menu()
    except ValueError as e:
        errors(e)
    menu()

def createAd():
    price = input("Введите цену объявления: ")
    esId = input("Введите ID имущества: ")
    try:
        contract.functions.createAd(int(price), int(esId)).transact({'from': login})
        print("Объявление успешно создано")
    except ValueError as e:
        errors(e)
    menu()

def changeEs():
    esId = input("Введите ID имущества: ")
    isActiveEs = input("Введите активна ли недвижимость (true/false): ")
    try:
        contract.functions.updateEstateStatus(int(esId), bool(isActiveEs)).transact({'from': login})
        print("Недвижимость успешно изменена")
    except ValueError as e:
        errors(e)
    menu()

def changeAd():
    adId = input("Введите ID объявления: ")
    esId = input("Введите ID имущества: ")
    adStatus = input("Введите статус: ")
    try:
        contract.functions.updateAdStatus(int(adId), int(esId), int(adStatus)).transact({'from': login})
        print("Объявление успешно изменено")
    except ValueError as e:
        errors(e)
    menu()

def buy():
    esID = input("Введите ID имущества: ")
    adID = input("Введите ID объявления: ")
    value = input("Введите средства: ")
    value = w3.to_wei(value, 'ether')
    try:
        contract.functions.buyEstate(int(esID), int(adID)).transact({'from': login, 'value': value, 'gasPrice': w3.to_wei('10', 'ether')})
        print("Недвижимость успешно куплена")
    except ValueError as e:
        errors(e)
    menu()

def getAllAds():
    for ad in contract.functions.getAds().call():
        print(f"Владелец: {ad[0]}\nЦена: {ad[2]}\n")
    menu()

def getAllEs():
    for es in contract.functions.getEstates().call():
        print(f"ID : {es[0]}\nЦена: {es[1]}\nОписание: {es[2]}\n")
    menu()

def getBalance():
    global login
    balance = contract.functions.getBalance().call({'from': login})
    print("Баланс:", balance / 10**18, "ETH")
    menu()



def goodPass(password):
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*()]', password):
        return False
    if re.search(r'(.)\1\1', password):
        return False
    if re.search(r'password|qwerty|123456|111111', password, re.IGNORECASE):
        return False
    return True

def main():
    global login
    choice = int(input("1.Войти\n2.Зарегистрироваться\n"))
    match choice:
        case 1: 
            login = input("Введите свой публичный ключ: ")
            password = input("Введите ваш пароль: ")
            try:
                w3.geth.personal.unlock_account(login, password)
                print("Успех ^_^")
                menu()
            except:
                print("Неверный логин или пароль")
                main()
        case 2:
            password = input("Введите ваш пароль: \n")
            if goodPass(password):
                newAcc = w3.eth.account.create(password)
                print(f"Ваш аккаунт: {newAcc.address}")
                balance = w3.to_wei(300,'ether')
                w3.eth.send_transaction({
                    'to': newAcc.address,
                    'value': balance,
                    'from': w3.eth.accounts[0],
                    'gas': 2000000,
                    'gasPrice': w3.eth.gas_price,
                })
                login = newAcc.address  
                print("Регистрация прошла успешно!")  
                main()
            else:
                print("Ну будем честны, пароль слабенький ()")
                main()    
        case _:
             print("АШИБКА АЛАРМ ТАКОГО НЕТ!")
             main()    

main()