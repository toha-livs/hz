import os
import datetime

os.environ.setdefault('FALCON_SETTINGS_MODULE', 'gusto_api.settings')

from gusto_api.utils import encrypt
from gusto_api.models import (
    User, Group, Permission,
    UserToken, Project, Staff, SuperUser, OpenTime)
from auth.utils import generate_users_tokens_by_group

#
# def fill_db():
#     """
#      Generate mock data
#
#     :return:
#     """
#
#     users_amount = 20
#     projects_amount = 5
#     groups_amount = projects_amount
#     permissions_amount = 2
#     tokens_amount = users_amount
#
#     counter = 0
#     users = []
#     for i in range(users_amount):
#         counter += 1
#         user = User(name='user' + str(counter),
#                      email='email' + str(counter) + '@example.com',
#                      password=encrypt(
#                          'email' + str(counter) + '@example.com' + 'tel' + str(counter) + 'user' + str(counter)),
#                      last_login=datetime.datetime.now(),
#                      date_created=datetime.datetime.now(),
#                      is_active=True,
#                      image='img' + str(counter),
#                      tel='tel' + str(counter)
#                      )
#         user.save()
#         users.append(user)
#     permissions = []
#     counter = 0
#     for i in range(permissions_amount):
#         counter += 1
#         permission = Permission(name='users',
#                                  access=1 if counter % 2 == 0 else 0)
#         permission.save()
#         permissions.append(permission)
#
#     # counter = 0
#     # groups_templates = []
#     # for i in range(amount):
#     #     counter += 1
#     #     first = randint(0, 50)
#     #     second = randint(50, 101)
#     #     ids = [x.pk for x in permissions[first:second]]
#     #     shuffle(ids)
#     #     groups_template = GroupTemplate(name='group_template' + str(counter),
#     #                                       permissions_ids=ids,
#     #                                       g_type='type' + str(counter))
#     #     groups_templates.append(groups_template)
#     #
#     # session.add_all(groups_templates)
#     # session.commit()
#
#     counter = 0
#     projects = []
#     for i in range(projects_amount):
#         counter += 1
#         name = str(counter) + '_project'
#         project = Project(name=name, domain='http://test_domain' + str(counter))
#         project.save()
#         projects.append(project)
#
#     counter = 0
#     groups = []
#     for i in range(groups_amount):
#         counter += 1
#         uss = [x for x in users[i * 4:i * 4 + 4]]
#         if i <= 2:
#             perm = [permissions[0]]
#         else:
#             perm = [permissions[1]]
#         group = Group(users=uss,
#                        project=projects[i],
#                        name='group' + str(counter),
#                        permissions=perm,
#                        is_owner=False)
#         group.save()
#         groups.append(group)
#
#     counter = 0
#     tokens = []
#     for i in range(tokens_amount):
#         counter += 1
#         token = UsersTokens(user=users[i],
#                             token='token' + str(counter))
#         token.save()
#         tokens.append(token)
#
#     update_user_tokens()
#
#
# def update_user_tokens():
#     for index, group in enumerate(Group.objects.all()):
#         generate_users_tokens_by_group(group)
#
#
# def fun():
#     currencies_amount = 10
#     currencies = []
#     counter = 0
#     for i in range(currencies_amount):
#         counter += 1
#         curr = Currencies(
#             name="curr_" + str(counter),
#             symbol="symbol_" + str(counter),
#             code="code_" + str(counter),
#             rate=counter,
#             rates=[counter],
#             last_update=datetime.datetime.now(),
#         )
#         curr.save()
#         currencies.append(curr)
#     print(currencies)
#     countries_amount = 10
#     counter = 0
#     countries = []
#     for i in range(countries_amount):
#         counter += 1
#         country = Countries(name='country_' + str(counter),
#                             iso2='iso2' + str(counter),
#                             dial_code='dial_code' + str(counter),
#                             priority=counter,
#                             currency=currencies[i]
#                             )
#         country.save()
#         countries.append(country)

#### anton
# def seed_cities():
    # currency1 = Currencies(name='Grivna', symbol='grn', code='380', rate=25, rates=27, last_update=datetime.datetime.now())
    # currency2 = Currencies(name='Dollar', symbol='usd', code='180', rate=1, rates=1,
    #                        last_update=datetime.datetime.now())
    # currency1.save()
    # currency2.save()
    #
    # coutry1 = Countries(name='Ukraine', iso2='380', dial_code='test1', priority=1, area_codes=[1, 2], currency=currency1)
    # coutry2 = Countries(name='USA', iso2='180', dial_code='test2', priority=2, area_codes=[3, 1], currency=currency2)
    # coutry1.save()
    # coutry2.save()

    # city1 = Cities(active=True, country_code='380', default=False, name='test1', lat=1.1213, lng=2.123, language={'en': 'test1'}, number_phone='325234123423', exist_store=True)
    # city2 = Cities(active=True, country_code='180', default=False, name='test2', lat=1.1213, lng=2.123,
    #                language={'ru': 'тест1'}, number_phone='3423', exist_store=False)
    # city1.save()
    # city2.save()

def permissions_create():
    # Permission(name='cities', access=0, descriptions='permission for read cities data').save()
    # Permission(name='cities', access=1, descriptions='permission for write cities data').save()
    Permission(name='working_time', access=0, description='permission for read working_time').save()
    Permission(name='working_time', access=1, description='permission for write working_time').save()



def create_super():
    super_user = User(name='super_admin', email='super_admin@gmail.com', tel='380663422234', password='qwerty')
    super_user.password = encrypt(super_user.email + super_user.tel + super_user.password)
    super_user.save()
    root = SuperUser(root=super_user)
    root.save()

def create_project():

    admin = User(name='admin_proj1', email='admin_proj1@gmail.com', tel='380634234', password='qwerty')
    admin.password = encrypt(admin.email + admin.tel + admin.password)
    admin.save()
    project = Project(name='first_project', domain='www.shluhy.com', owner=admin, p_type='restic').save()
    group = Group(name='admin_group', users=[admin], project=project, permissions=[permission for permission in Permission.objects.filter(name='cities', access__in=[0,1])]).save()


def staff_create():
    project = Project.objects.filter(name='first_project').first()
    prj_admin = User.objects.filter(name='admin_proj1').first()
    stf = User(name='staff_proj1', email='staff_proj1@gmail.com', tel='3806454234', password='qwerty')
    stf.password = encrypt(stf.email + stf.tel + stf.password)
    stf.save()

    staff = Staff(owner=prj_admin, staff_list=[stf]).save()

    group_read = Group(name='Read working_time', users=[stf], project=project, permissions=[permission for permission in Permission.objects.filter(name='working_time', access=0)]).save()

def create_WT():
    OpenTime(day=0, open_hours=9, open_minutes=0, close_minutes=30, close_hours=23, project=Project.objects.filter(name='first_project').first()).save()

def gen_token():
    users = [user.generate_token() for user in User.objects.all()]

if __name__ == '__main__':
    # permissions_create()
    # create_super()
    # create_project()
    # create_WT()
    # staff_create()
    gen_token()
    # pass

    # fun()
