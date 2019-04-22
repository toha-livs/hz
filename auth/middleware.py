import falcon

from falcon_cors import CORS

from auth.utils import get_user_token

cors = CORS(allow_all_origins=True, allow_all_headers=True, allow_all_methods=True)

CORSMiddleware = cors.middleware


class BaseMiddleware:
    token = None

    def check_cors(self, req):
        return req.method == 'OPTIONS'

    def check_token(self):
        self.token = get_user_token(self.token)
        return bool(self.token)


class AuthMiddleware(BaseMiddleware):
    def process_request(self, req, resp):
        token = req.get_header('Authorization')
        if token:
            token_type, self.token = token.strip().split()

    def process_resource(self, req, resp, resource, params):
        if not self.check_cors(req):
            if resource.use_token and not self.check_token():
                raise falcon.HTTPUnauthorized
            else:
                resource.storage.update({'token': self.token})
