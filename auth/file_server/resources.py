from falcon_core.resources import Resource

from auth.utils import send_files_to_file_server


class SendFilesResource(Resource):
    use_token = True

    def on_post(self, request, response, **kwargs):
        """
        Call util for sending files to the file-server
        url /files/
        """
        send_files_to_file_server(request, response)
