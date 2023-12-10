import re
def check_login(login):
    if re.search('\W', login):
        return False
    else:
        return True

def check_password(password):
    if re.search('\W', password):
        return 'Пароль должен состоять только из букв и цифр'
    if len(password) < 8:
        return 'Длина пароля должна быть не менее 8 символов'
    else:
        return 'Поздравляю ты зарегистрирован!'


