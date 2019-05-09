from falcon_core.routes import route

from .resources import SendFilesResource

routes = [
    route('', SendFilesResource()),
]
