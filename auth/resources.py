from falcon import HTTP_404


class Resource:
    use_token = False
    storage = {}

    def on_get(self, request, response, **kwargs):
        response.status = HTTP_404

    def on_post(self, request, response, **kwargs):
        response.status = HTTP_404

    def on_put(self, request, response, **kwargs):
        response.status = HTTP_404

    def on_delete(self, request, response, **kwargs):
        response.status = HTTP_404
