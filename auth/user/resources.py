from auth.resources import Resource


class UsersResource(Resource):
    use_token = True

    def on_get(self, request, response, **kwargs):

        response.media = get_univ_filter(Users, request.params)
        response.status = falcon.HTTP_200

    def on_post(self, req, resp, **kwargs):
        post_create_user(req.stream, resp)


class UserResource(Resource):
    use_token = True

    def on_get(self, request, response, **kwargs):
        get_request_util(Users, kwargs.get('user_id'), response)

    def on_put(self, request, response, **kwargs):
        put_request_util(Users, request.stream, kwargs.get('user_id'), response)

    def on_delete(self, request, response, **kwargs):
        delete_request_util(Users, kwargs.get('user_id'), response)

