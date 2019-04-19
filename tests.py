import os

from auth.utils import encrypt_password

from gusto_api.models import Users, Permissions, UsersTokens, Groups

os.environ.setdefault('FALCON_CORE_SETTINGS_MODULE', 'gusto_api.settings')

Users.objects.all().delete()

for i in range(1, 11):
    name = f'name{i}'
    surname = f'surname{i}'
    email = f'email{i}@ga.com'
    tel = f'tel{i}'
    password = f'pass{i}'
    user = Users(name=name, surname=surname, email=email, tel=tel)
    user.password = encrypt_password(user, password)
    user.save()

Permissions.objects.all().delete()

perm_users_r = Permissions(name='users', access=0).save()
perm_users_w = Permissions(name='users', access=1).save()

Groups.objects.all().delete()

group1 = Groups(name='group1')
group1.permissions.append(perm_users_r)
group1.permissions.append(perm_users_w)
group2 = Groups(name='group2')
group2.permissions.append(perm_users_r)
group2.permissions.append(perm_users_w)

for index, user in enumerate(Users.objects.all(), 1):
    group1.users.append(user)
    group2.users.append(user)

group1.save()
group2.save()



