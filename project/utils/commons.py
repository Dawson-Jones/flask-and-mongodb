from werkzeug.routing import BaseConverter


class Reconverter(BaseConverter):
    def __init__(self, url_map, regex):
        super().__init__(url_map)
        self.regex = regex
