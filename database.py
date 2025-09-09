# Напишем бд на json, чтобы хранить всех учеников
# Сначала напишем то, как будет выглядеть структура бд
"""
{
    "students": [
        {"id": 1408266288, "name": "Арсений", "surname": "Белокуров", "age": 16, "paired_with": "6437541376"}
        {"id": 6437541376, "name": "Елисей", "surname": "Николаев", "age": 16, "paired_with": "1408266288"}
    ]
}
"""

import json

class Database:
    """
    A class to interact with the student database stored in 'database.json'.
    """

    def __init__(self, filename='database.json'):
        """
        Initializes the Database object.
        
        Args:
            filename (str): The filename of the database. Defaults to 'database.json'.
        """
        self.filename = filename
        self.data = self.load_database()

    def add_or_update_user(self, user_id: int, username: str, first_name: str, last_name: str) -> None:
        """
        Adds or updates a user in the database.
        
        Args:
            user_id (int): The ID of the user.
            username (str): The username of the user.
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
        """
        user = {
            'id': user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        }
        if 'users' not in self.data:
            self.data['users'] = []
        existing_user = next((u for u in self.data['users'] if u['id'] == user_id), None)
        if existing_user:
            existing_user.update(user)
        else:
            self.data['users'].append(user)
        self.save_database(self.data)

    def get_all_users(self) -> list:
        """
        Gets all users from the database.
        
        Returns:
            list: A list of all users.
        """
        return self.data.get('users', [])
    
    def get_user_by_username(self, username: str) -> dict:
        """
        Gets a user by their username.
        
        Args:
            username (str): The username of the user.
        
        Returns:
            dict: The user data, or None if not found.
        """
        if 'users' in self.data:
            for user in self.data['users']:
                if user['username'].lower() == username.lower():
                    return user
            return None
    
    def get_users_by_first_name(self, first_name: str) -> list:
        """
        Gets all users with the specified first name.
        
        Args:
            first_name (str): The first name of the users.
        
        Returns:
            list: A list of users with the specified first name.
        """
        if 'users' in self.data:
            return [user for user in self.data['users'] if user['first_name'].lower() == first_name.lower()]
        else:
            return []

    def load_database(self) -> dict:
        """
        Loads the database from the specified file.
        
        Returns:
            dict: The loaded database.
        """
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"students": []}

    def save_database(self, data: dict) -> None:
        """
        Saves the database to the specified file.
        
        Args:
            data (dict): The database to save.
        """
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def add_student(self, student_id: int, name: str, surname: str, age: int) -> None:
        """
        Adds a new student to the database.
        
        Args:
            student_id (int): The ID of the student.
            name (str): The name of the student.
            surname (str): The surname of the student.
            age (int): The age of the student.
        """
        new_student = {"id": student_id, "name": name, "surname": surname, "age": age, "paired_with": None}
        self.data["students"].append(new_student)
        self.save_database(self.data)

    def remove_student(self, student_id: int) -> None:
        """
        Removes a student from the database.
        
        Args:
            student_id (int): The ID of the student to remove.
        """
        data = self.load_database()
        data["students"] = [student for student in data["students"] if student["id"] != student_id]
        self.save_database(data)

    def update_student(self, student_id: int, paired_with: int) -> None:
        """
        Updates a student's paired_with field in the database.
        
        Args:
            student_id (int): The ID of the student to update.
            paired_with (int): The ID to pair the student with.
        """
        data = self.load_database()
        for student in data["students"]:
            if student["id"] == student_id:
                student["paired_with"] = paired_with
                break
        self.save_database(data)

    def get_student(self, student_id: int) -> dict:
        """
        Retrieves a student from the database by their ID.
        
        Args:
            student_id (int): The ID of the student to retrieve.
        
        Returns:
            dict: The student's data, or None if not found.
        """
        data = self.load_database()
        for student in data["students"]:
            if student["id"] == student_id:
                return student
        return None

