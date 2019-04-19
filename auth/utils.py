from falcon_core.utils import encrypt_sha256_with_secret_key

from gusto_api.models import UsersTokens


def encrypt_password(user, password):
    return encrypt_sha256_with_secret_key(user.email + user.tel + password)


def get_user_token(token):
    return UsersTokens.objects.filter(token=token).first()
