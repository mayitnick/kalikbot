import json
import os

class Database:
    def __init__(self, filename='students.json'):
        self.filename = filename
        self.data = {"students": []}  # корневой объект
        self.load()

    def load(self):
        """Загружает БД из файла или создаёт новый файл."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    self.data = json.load(file)
                    if "students" not in self.data:
                        # если старая структура — пересоздать
                        self.data = {"students": [], "groups": []}
            except json.JSONDecodeError:
                print("Ошибка JSON. Создаю новую базу.")
                self.data = {"students": []}
                self.save()
        else:
            print("Файл не найден. Создаю новый.")
            self.save()

    def save(self):
        """Сохраняет БД в файл."""
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def add_user(self, telegram_id, telegram_username, full_name,
                 user_type="guest", group=None, age=None):
        """Добавляет нового пользователя в БД."""
        existing = self.get_user_by_id(telegram_id)
        if existing:
            print(f"Пользователь {full_name} ({telegram_id}) уже есть в БД.")
            return existing

        user = {
            "telegram_id": telegram_id,
            "telegram_username": telegram_username,
            "full_name": full_name,
            "type": user_type,  # guest | student | curator | admin | founder
            "group": group,
            "age": age,
            "duty_info": None if user_type == "student" else None
        }

        self.data["students"].append(user)
        self.save()
        print(f"Пользователь {full_name} ({telegram_id}) добавлен как {user_type}.")
        return user

    def upgrade_user(self, telegram_id, new_type, group=None):
        """Меняет тип пользователя (например, guest -> student)."""
        user = self.get_user_by_id(telegram_id)
        if not user:
            print("Пользователь не найден.")
            return None

        user["type"] = new_type
        if new_type == "student":
            user["group"] = group
            if user["duty_info"] is None:
                user["duty_info"] = {
                    "last_duty": None,
                    "amount_of_duties": 0,
                    "pair_id": None,
                    "preferences": []
                }
        elif new_type in ["curator", "admin", "founder"]:
            user["group"] = group if new_type == "curator" else None
            user["duty_info"] = None

        self.save()
        print(f"Пользователь {user['first_name']} теперь {new_type}.")
        return user

    def get_user_by_id(self, telegram_id):
        try:
            for user in self.data["students"]:
                if user["telegram_id"] == int(telegram_id):
                    return user
            return None
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def get_user_by_username(self, telegram_username):
        for user in self.data["students"]:
            if user["telegram_username"] == telegram_username:
                return user
        return None

    def get_all_users(self):
        return self.data["students"]
    
    def upgrade_to_student(self, telegram_id, group):
        """Апгрейд пользователя до студента."""
        return self.upgrade_user(telegram_id, new_type="student", group=group)

    def upgrade_to_curator(self, telegram_id, group):
        """Апгрейд пользователя до куратора."""
        return self.upgrade_user(telegram_id, new_type="curator", group=group)

    def upgrade_to_admin(self, telegram_id):
        """Апгрейд пользователя до админа."""
        return self.upgrade_user(telegram_id, new_type="admin")

    def upgrade_to_founder(self, telegram_id):
        """Апгрейд пользователя до основателя."""
        return self.upgrade_user(telegram_id, new_type="founder")
    
    def update_user_field(self, telegram_id, field, value):
        """Обновляет или добавляет указанное поле у пользователя."""
        user = self.get_user_by_id(telegram_id)
        if not user:
            print("Пользователь не найден.")
            return None

        old_value = user.get(field, None)
        user[field] = value
        self.save()
        print(f"Поле '{field}' пользователя {user.get('full_name', telegram_id)} изменено: {old_value} -> {value}")
        return user
    
    # Теперь сделаем работу с группами
    # Подсказка структуры
    """
    "groups": [
        {
            "group": "IS-11-25",
            "tg_group_id": 2492979822,
            "curator": 6862396551,
            "students": [1408266288],
            "duty": []
        }
    ]
    """
    def create_group(self, group_name):
        if group_name not in [group["group"] for group in self.data["groups"]]:
            self.data["groups"].append({
                "group": group_name,
                "tg_group_id": None,
                "curator": None,
                "students": [],
                "duty": []
                })
            self.save()
            if self.data["groups"][-1]["group"] == group_name:
                print(f"Группа {group_name} создана.")
                return True
            else:
                print("Ошибка создания группы.")
                return False
        else:
            if self.get_group_by_name(group_name)["tg_group_id"] is None:
                print(f"Группа {group_name} уже существует, но не привязана к Telegram.")
                return False
            else:
                print(f"Группа {group_name} уже существует и привязана к Telegram.")
                return True
    def get_group_by_name(self, group_name):
        for group in self.data["groups"]:
            if group["group"] == group_name:
                return group
        return None
    def get_group_by_id(self, group_id):
        for group in self.data["groups"]:
            if group["tg_group_id"] == group_id:
                return group
        return None
    def get_group_by_curator(self, curator_id):
        for group in self.data["groups"]:
            if group["curator"] == curator_id:
                return group
        return None
    def set_curator(self, group_name, curator_id):
        if group_name in [group["group"] for group in self.data["groups"]]:
            group = self.get_group_by_name(group_name)
            if group["curator"] is None:
                group["curator"] = curator_id
                self.save()
                print(f"Куратор для группы {group_name} установлен.")
                return True
            else:
                if group["curator"] == curator_id:
                    print(f"Куратор для группы {group_name} уже установлен.")
                    return True
                else:
                    print(f"Куратор для группы {group_name} уже установлен.")
                    return False
    def set_duty(self, group_name, duty):
        if group_name in [group["group"] for group in self.data["groups"]]:
            group = self.get_group_by_name(group_name)
            group["duty"] = duty
            self.save()
            print(f"Дежурные для группы {group_name} установлены.")
            return True
    def add_student(self, group_name, student_id):
        if group_name in [group["group"] for group in self.data["groups"]]:
            group = self.get_group_by_name(group_name)
            if student_id not in group["students"]:
                group["students"].append(student_id)
                # Дополнительно обновляем группу в студенте
                self.update_user_field(student_id, "group", group_name)
                
                self.save()
                print(f"Студент {student_id} добавлен в группу {group_name}.")
                return True
    def set_tg_group_id(self, group_name, tg_group_id):
        if group_name in [group["group"] for group in self.data["groups"]]:
            group = self.get_group_by_name(group_name)
            group["tg_group_id"] = tg_group_id
            self.save()
            print(f"Telegram ID группы {group_name} установлен.")
            return True
    def remove_student(self, group_name, student_id):
        if group_name in [group["group"] for group in self.data["groups"]]:
            group = self.get_group_by_name(group_name)
            if student_id in group["students"]:
                group["students"].remove(student_id)
                self.save()
                print(f"Студент {student_id} удален из группы {group_name}.")
                return True
    def get_all_groups(self):
        return self.data["groups"]