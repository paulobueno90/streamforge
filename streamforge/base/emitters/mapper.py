
class Mapper:
    def __init__(self):
        self._mappings = {}

    def register(self, name, mapping):
        self._mappings[name] = mapping

    def transform(self, record, name):
        mapping = self._mappings[name]
        return {
            out_key: getattr(record, in_key)
            for in_key, out_key in mapping.items()
        }