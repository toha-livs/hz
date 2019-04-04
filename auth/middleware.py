import falcon

from falcon_cors import CORS
from gusto_api.models import UsersTokens
from src.auth.utils import token_exists

cors = CORS(allow_origins_list=['*'], allow_all_origins=True, allow_all_headers=True, allow_all_methods=True)


CORSMiddleware = cors.middleware


class BaseMiddleware:
    def check_cors(self, req: falcon.Request):
        return (req.get_header('ACCESS-CONTROL-REQUEST-METHOD')
                and req.get_header('ACCESS-CONTROL-REQUEST-HEADERS'))
    def verify_token(self, instance):
        token = UsersTokens.objects.filter(token=instance.token).first()
        return True if bool(token) else False


class AuthMiddleware(BaseMiddleware):
    token = None

    def process_request(self, req, resp):
        # 'Bearer token'
        token = req.get_header('Authorization')
        if token:
            t_type, token = token.split()
        self.token = token

    def process_resource(self, req: falcon.Request, resp: falcon.Response, resource, params):
        if not self.check_cors(req) and resource.use_token:
            if self.verify_token(self):
                resource.storage.update({'token': self.token})
            else:
                raise falcon.HTTPUnauthorized('Token is not exists or not set.')
