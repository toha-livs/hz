from auth.resources import Resource
import falcon
from gusto_api.models import Groups, Projects, Users, Permissions
import json


def set_data(group, data):
    try:
        for key, value in data.items():
            if key == "project":
                project = Projects.objects.filter(id=value).first()
                if project:
                    setattr(group, key, project)
            elif key == "users" or key == "permissions" and isinstance(value, list):
                objects = []
                for object_id in value:
                    if len(object_id) != 24:
                        continue
                    if key == "users":
                        obj = Users.objects.filter(id=object_id).first()
                    else:
                        obj = Permissions.objects.filter(id=object_id).first()
                    if obj:
                        objects.append(obj)
                setattr(group, key, objects)
            else:
                setattr(group, key, value)
        return group
    except Exception as e:
        print(e)
        return None


def filter_data(data):
    new_data = {}
    for key, value in data.items():
        if value == 'true':
            new_data[key] = True
        elif value == 'false':
            new_data[key] = False
        else:
            new_data[key] = value
    return new_data


class GroupsResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        print(kwargs)
        fields = filter_data(req.params)
        sort = fields.pop('sort', 'id')
        if sort not in Groups.fields:
            sort = 'id'
        off_set = int(fields.pop('offset', 0))
        limit = int(fields.pop('limit', 0))
        query_list = Groups.objects.filter(**fields).order_by(sort)
        if limit:
            query_list = query_list[off_set:off_set + limit]
        try:
            resp.media = json.loads(query_list.to_json())
            resp.status = falcon.HTTP_200
        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_404

    def on_post(self, req, resp, **kwargs):
        post_data = req.stream.read()
        if post_data:
            post_data = json.loads(post_data)
        else:
            post_data = {}
        group = set_data(Groups(), post_data)
        if group:
            group.save()
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_500


class GroupResource(Resource):
    use_token = True

    def on_get(self, req, resp, **kwargs):
        try:
            if 'id' in kwargs.keys():
                group = Groups.objects.filter(**kwargs).first()
            elif 'project_id' in kwargs.keys():
                keys = {'project': kwargs['project_id']}
                group = Groups.objects.filter(**keys).first()
            else:
                group = None
            if group is None:
                raise Exception("Group not found")
            resp.media = json.loads(group.to_json())
            resp.status = falcon.HTTP_200
        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_404

    def on_put(self, req, resp, **kwargs):
        if 'id' not in kwargs.keys():
            resp.status = falcon.HTTP_404
            return
        group = Groups.objects.filter(**kwargs).first()
        if not group:
            resp.status = falcon.HTTP_400
            return
        update_data = req.stream.read()
        if update_data:
            update_data = json.loads(update_data)
        else:
            update_data = {}

        group = set_data(group, update_data)
        if group:
            group.save()
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_500

    def on_delete(self, req, resp, **kwargs):
        if 'id' not in kwargs.keys():
            resp.status = falcon.HTTP_404
            return
        group = Groups.objects.filter(**kwargs).first()
        if not group:
            resp.status = falcon.HTTP_400
            return
        group.delete()
        resp.status = falcon.HTTP_200
