import json
import os

class Permissions:
    def __init__(self):
        # Получаем путь к корневой папке проекта
        base_dir = os.path.abspath(os.path.dirname(__file__))
        # Строим путь к файлу permissions.json в корне проекта
        json_path = os.path.join(base_dir, '..', 'permissions.json')
        json_path = os.path.normpath(json_path)

        with open(json_path) as json_file:
            self.permissions = json.load(json_file)

    def check_for_permissions(self, user_type, permission):
        if user_type in self.permissions:
            if permission in self.permissions[user_type]:
                return True
            else:
                return False
        else:
            return False
