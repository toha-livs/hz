import os

from auth.utils import encrypt_password

from gusto_api.models import User, Permission, UserToken, Group

os.environ.setdefault('FALCON_CORE_SETTINGS_MODULE', 'gusto_api.settings')

User.objects.all().delete()

for i in range(1, 11):
    name = f'name{i}'
    surname = f'surname{i}'
    email = f'email{i}@ga.com'
    tel = f'tel{i}'
    password = f'pass{i}'
    user = User(name=name, surname=surname, email=email, tel=tel)
    user.password = encrypt_password(user, password)
    user.save()

Permissi.objects.all().delete()

perm_users_r = Permission(name='users', access=0).save()
perm_users_w = Permission(name='users', access=1).save()

Group.objects.all().delete()

group1 = Group(name='group1')
group1.permissions.append(perm_users_r)
group1.permissions.append(perm_users_w)
group2 = Group(name='group2')
group2.permissions.append(perm_users_r)
group2.permissions.append(perm_users_w)

for index, user in enumerate(User.objects.all(), 1):
    group1.users.append(user)
    group2.users.append(user)

group1.save()
group2.save()

for user in User.objects.all():
    user.generate_token()
