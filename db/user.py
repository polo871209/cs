import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from . import DB


@dataclass
class User:
    user_id: int
    username: str
    email: str
    full_name: str
    age: int
    city: str
    country: str
    occupation: str
    department: str
    salary: float
    join_date: str
    is_active: bool
    last_login: str


class UserDB:
    """
    Database for storing user information.
    Provides mock user data that can be used as a tool in the chat application.
    """

    def __init__(self):
        self.db_path = DB
        self.init_database()
        self.insert_mock_data()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections with error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def init_database(self):
        """Initialize the database and create user table if it doesn't exist"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        full_name TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        city TEXT NOT NULL,
                        country TEXT NOT NULL,
                        occupation TEXT NOT NULL,
                        department TEXT NOT NULL,
                        salary REAL NOT NULL,
                        join_date DATE NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        last_login DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create indexes for faster queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_users_username 
                    ON users(username)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_users_email 
                    ON users(email)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_users_department 
                    ON users(department)
                """)

                conn.commit()
        except sqlite3.Error as e:
            print(f"❌ User database initialization error: {e}")
            raise

    def insert_mock_data(self):
        """Insert mock user data if the table is empty"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Check if data already exists
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]

                if count > 0:
                    return  # Data already exists

                # Mock data
                mock_users = [
                    (
                        "john_doe",
                        "john.doe@company.com",
                        "John Doe",
                        28,
                        "New York",
                        "USA",
                        "Software Engineer",
                        "Engineering",
                        85000,
                        "2022-01-15",
                        True,
                        "2024-01-10 09:30:00",
                    ),
                    (
                        "sarah_wilson",
                        "sarah.wilson@company.com",
                        "Sarah Wilson",
                        32,
                        "London",
                        "UK",
                        "Product Manager",
                        "Product",
                        95000,
                        "2021-03-20",
                        True,
                        "2024-01-09 14:20:00",
                    ),
                    (
                        "mike_chen",
                        "mike.chen@company.com",
                        "Mike Chen",
                        26,
                        "San Francisco",
                        "USA",
                        "Data Scientist",
                        "Analytics",
                        90000,
                        "2022-06-10",
                        True,
                        "2024-01-10 11:15:00",
                    ),
                    (
                        "emma_garcia",
                        "emma.garcia@company.com",
                        "Emma Garcia",
                        29,
                        "Madrid",
                        "Spain",
                        "UX Designer",
                        "Design",
                        70000,
                        "2021-11-05",
                        True,
                        "2024-01-08 16:45:00",
                    ),
                    (
                        "alex_kumar",
                        "alex.kumar@company.com",
                        "Alex Kumar",
                        35,
                        "Mumbai",
                        "India",
                        "DevOps Engineer",
                        "Engineering",
                        75000,
                        "2020-08-12",
                        True,
                        "2024-01-10 08:00:00",
                    ),
                    (
                        "lisa_brown",
                        "lisa.brown@company.com",
                        "Lisa Brown",
                        31,
                        "Toronto",
                        "Canada",
                        "Marketing Manager",
                        "Marketing",
                        80000,
                        "2021-09-18",
                        True,
                        "2024-01-09 10:30:00",
                    ),
                    (
                        "david_lee",
                        "david.lee@company.com",
                        "David Lee",
                        27,
                        "Seoul",
                        "South Korea",
                        "Frontend Developer",
                        "Engineering",
                        72000,
                        "2022-04-25",
                        True,
                        "2024-01-10 13:20:00",
                    ),
                    (
                        "anna_mueller",
                        "anna.mueller@company.com",
                        "Anna Mueller",
                        33,
                        "Berlin",
                        "Germany",
                        "QA Engineer",
                        "Quality",
                        68000,
                        "2021-07-08",
                        True,
                        "2024-01-09 15:10:00",
                    ),
                    (
                        "carlos_rodriguez",
                        "carlos.rodriguez@company.com",
                        "Carlos Rodriguez",
                        30,
                        "Mexico City",
                        "Mexico",
                        "Backend Developer",
                        "Engineering",
                        78000,
                        "2022-02-14",
                        True,
                        "2024-01-10 07:45:00",
                    ),
                    (
                        "sophie_martin",
                        "sophie.martin@company.com",
                        "Sophie Martin",
                        34,
                        "Paris",
                        "France",
                        "HR Manager",
                        "Human Resources",
                        85000,
                        "2020-12-03",
                        True,
                        "2024-01-08 12:00:00",
                    ),
                    (
                        "james_taylor",
                        "james.taylor@company.com",
                        "James Taylor",
                        29,
                        "Sydney",
                        "Australia",
                        "Sales Manager",
                        "Sales",
                        82000,
                        "2021-05-22",
                        False,
                        "2023-12-15 17:30:00",
                    ),
                    (
                        "maria_santos",
                        "maria.santos@company.com",
                        "Maria Santos",
                        25,
                        "São Paulo",
                        "Brazil",
                        "Junior Developer",
                        "Engineering",
                        55000,
                        "2023-01-09",
                        True,
                        "2024-01-10 09:00:00",
                    ),
                    (
                        "hassan_ali",
                        "hassan.ali@company.com",
                        "Hassan Ali",
                        36,
                        "Dubai",
                        "UAE",
                        "Solutions Architect",
                        "Engineering",
                        110000,
                        "2019-10-15",
                        True,
                        "2024-01-09 11:30:00",
                    ),
                    (
                        "yuki_tanaka",
                        "yuki.tanaka@company.com",
                        "Yuki Tanaka",
                        28,
                        "Tokyo",
                        "Japan",
                        "Mobile Developer",
                        "Engineering",
                        80000,
                        "2022-03-07",
                        True,
                        "2024-01-10 14:15:00",
                    ),
                    (
                        "nina_petrov",
                        "nina.petrov@company.com",
                        "Nina Petrov",
                        32,
                        "Moscow",
                        "Russia",
                        "Business Analyst",
                        "Analytics",
                        65000,
                        "2021-08-30",
                        True,
                        "2024-01-09 08:45:00",
                    ),
                ]

                cursor.executemany(
                    """
                    INSERT INTO users (username, email, full_name, age, city, country, occupation, 
                                     department, salary, join_date, is_active, last_login)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    mock_users,
                )

                conn.commit()
                print("🎭 Mock user data inserted successfully!")
        except sqlite3.Error as e:
            print(f"❌ Error inserting mock data: {e}")

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        if not user_id:
            return None
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT user_id, username, email, full_name, age, city, country, 
                           occupation, department, salary, join_date, is_active, last_login
                    FROM users WHERE user_id = ?
                """,
                    (user_id,),
                )
                row = cursor.fetchone()
                return User(*row) if row else None
        except sqlite3.Error as e:
            print(f"❌ Error getting user by ID: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        if not username:
            return None
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT user_id, username, email, full_name, age, city, country, 
                           occupation, department, salary, join_date, is_active, last_login
                    FROM users WHERE username = ?
                """,
                    (username,),
                )
                row = cursor.fetchone()
                return User(*row) if row else None
        except sqlite3.Error as e:
            print(f"❌ Error getting user by username: {e}")
            return None

    def get_users_by_department(self, department: str) -> List[User]:
        """Get all users in a specific department"""
        if not department:
            return []
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT user_id, username, email, full_name, age, city, country, 
                           occupation, department, salary, join_date, is_active, last_login
                    FROM users WHERE department = ? AND is_active = 1
                    ORDER BY full_name
                """,
                    (department,),
                )
                rows = cursor.fetchall()
                return [User(*row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Error getting users by department: {e}")
            return []

    def get_users_by_country(self, country: str) -> List[User]:
        """Get all users from a specific country"""
        if not country:
            return []
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT user_id, username, email, full_name, age, city, country, 
                           occupation, department, salary, join_date, is_active, last_login
                    FROM users WHERE country = ? AND is_active = 1
                    ORDER BY full_name
                """,
                    (country,),
                )
                rows = cursor.fetchall()
                return [User(*row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Error getting users by country: {e}")
            return []

    def search_users(self, query: str) -> List[User]:
        """Search users by name, username, email, or occupation"""
        if not query or not query.strip():
            return []
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                search_term = f"%{query.strip()}%"
                cursor.execute(
                    """
                    SELECT user_id, username, email, full_name, age, city, country, 
                           occupation, department, salary, join_date, is_active, last_login
                    FROM users 
                    WHERE (full_name LIKE ? OR username LIKE ? OR email LIKE ? OR occupation LIKE ?)
                    AND is_active = 1
                    ORDER BY full_name
                """,
                    (search_term, search_term, search_term, search_term),
                )

                rows = cursor.fetchall()
                return [User(*row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Error searching users: {e}")
            return []

    def get_all_users(self, active_only: bool = True) -> List[User]:
        """Get all users"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if active_only:
                    cursor.execute("""
                        SELECT user_id, username, email, full_name, age, city, country, 
                               occupation, department, salary, join_date, is_active, last_login
                        FROM users WHERE is_active = 1
                        ORDER BY full_name
                    """)
                else:
                    cursor.execute("""
                        SELECT user_id, username, email, full_name, age, city, country, 
                               occupation, department, salary, join_date, is_active, last_login
                        FROM users
                        ORDER BY full_name
                    """)
                rows = cursor.fetchall()
                return [User(*row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Error getting all users: {e}")
            return []

    def get_department_stats(self) -> Dict[str, Any]:
        """Get statistics by department"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT department, 
                           COUNT(*) as employee_count,
                           AVG(salary) as avg_salary,
                           MIN(salary) as min_salary,
                           MAX(salary) as max_salary,
                           AVG(age) as avg_age
                    FROM users 
                    WHERE is_active = 1
                    GROUP BY department
                    ORDER BY employee_count DESC
                """)
                rows = cursor.fetchall()
                return [
                    {
                        "department": row[0],
                        "employee_count": row[1],
                        "avg_salary": round(row[2], 2),
                        "min_salary": row[3],
                        "max_salary": row[4],
                        "avg_age": round(row[5], 1),
                    }
                    for row in rows
                ]
        except sqlite3.Error as e:
            print(f"❌ Error getting department stats: {e}")
            return []

    def get_country_distribution(self) -> Dict[str, int]:
        """Get user distribution by country"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT country, COUNT(*) as user_count
                    FROM users 
                    WHERE is_active = 1
                    GROUP BY country
                    ORDER BY user_count DESC
                """)
                rows = cursor.fetchall()
                return {row[0]: row[1] for row in rows}
        except sqlite3.Error as e:
            print(f"❌ Error getting country distribution: {e}")
            return {}
