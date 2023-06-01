from django.contrib.auth import get_user_model

User = get_user_model()


def validate_signup(data):
    if not all([i for i in data.values()]):
        return False, "You Must Provide The Whole Data"
    try:
        User.objects.get(username=data["username"])
        return False, "The Username Is Not Available , Try Another"
    except:
        if data["password1"] != data["password2"]:
            return False, "The Given Passwords Don't Match , Please Type Them Correctly"
        if len(data["password1"]) < 8:
            return False, "A Password With 8 Or More Letters,Digits Or Symbols Is Required"
        return True, ''


def validate_login(data):
    if not all([i for i in data.values()]):
        return False, "You Must Provide The Whole Data"
    return True, ''
