class Editor:
    def __init__(self, level = None):
        self._data = {"tiles": [],
                      "particles": [],
                      "titles": [],
                      "start_pos": None}

        if level is not None:
            self._data = level.get_data()

    def add_object(self, section, obj):
        """add object to data"""
        self._data[section].append(obj)

    def delete_object(self, section, obj):
        """remove object from data"""
        obj.delete()
        self._data[section].remove(obj)
