import os
import datetime

os.environ.setdefault('FALCON_SETTINGS_MODULE', 'gusto_api.settings')

from gusto_api.utils import encrypt
from gusto_api.models import (
    Users, Groups, Permissions,
    UsersTokens, Projects, LanguageTemplate
)
from auth.utils import generate_users_tokens_by_group


def fill_db():
    """
     Generate mock data

    :return:
    """

    users_amount = 20
    projects_amount = 5
    groups_amount = projects_amount
    permissions_amount = 2
    tokens_amount = users_amount

    counter = 0
    users = []
    for i in range(users_amount):
        counter += 1
        user = Users(name='user' + str(counter),
                     email='email' + str(counter) + '@example.com',
                     password=encrypt(
                         'email' + str(counter) + '@example.com' + 'tel' + str(counter) + 'user' + str(counter)),
                     last_login=datetime.datetime.now(),
                     date_created=datetime.datetime.now(),
                     is_active=True,
                     image='img' + str(counter),
                     tel='tel' + str(counter)
                     )
        user.save()
        users.append(user)
    permissions = []
    counter = 0
    for i in range(permissions_amount):
        counter += 1
        permission = Permissions(name='users',
                                 access=1 if counter % 2 == 0 else 0)
        permission.save()
        permissions.append(permission)

    # counter = 0
    # groups_templates = []
    # for i in range(amount):
    #     counter += 1
    #     first = randint(0, 50)
    #     second = randint(50, 101)
    #     ids = [x.pk for x in permissions[first:second]]
    #     shuffle(ids)
    #     groups_template = GroupsTemplates(name='group_template' + str(counter),
    #                                       permissions_ids=ids,
    #                                       g_type='type' + str(counter))
    #     groups_templates.append(groups_template)
    #
    # session.add_all(groups_templates)
    # session.commit()

    counter = 0
    projects = []
    for i in range(projects_amount):
        counter += 1
        name = LanguageTemplate(en='name' + str(counter), ru="имя" + str(counter))
        project = Projects(name=name, domain='http://test_domain' + str(counter))
        project.save()
        projects.append(project)

    counter = 0
    groups = []
    for i in range(groups_amount):
        counter += 1
        uss = [x for x in users[i * 4:i * 4 + 4]]
        if i <= 2:
            perm = [permissions[0]]
        else:
            perm = [permissions[1]]
        group = Groups(users=uss,
                       project=projects[i],
                       name='group' + str(counter),
                       permissions=perm,
                       is_owner=False)
        group.save()
        groups.append(group)

    counter = 0
    tokens = []
    for i in range(tokens_amount):
        counter += 1
        token = UsersTokens(user=users[i],
                            token='token' + str(counter))
        token.save()
        tokens.append(token)

    update_user_tokens()


def update_user_tokens():
    for index, group in enumerate(Groups.objects.all()):
        generate_users_tokens_by_group(group)


if __name__ == '__main__':
    # fill_db()
    # print(encrypt('email1@example.com'+'tel1'+'user1'))
    for i in (Users.objects.filter(name='user1').first().groups):
        print(i)