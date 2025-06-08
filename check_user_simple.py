import sqlite3

def check_user_data():
    try:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        # Check the specific user
        cursor.execute('SELECT id, first_name, last_name, email FROM users WHERE id = ?', 
                      ('2e4f6d87-797c-4af3-a8f4-73e37acbf57a',))
        user = cursor.fetchone()
        
        if user:
            print(f"User ID: {user[0]}")
            print(f"First Name: '{user[1]}'")
            print(f"Last Name: '{user[2]}'")
            print(f"Email: {user[3]}")
            print(f"First name length: {len(user[1]) if user[1] else 0}")
            print(f"Last name length: {len(user[2]) if user[2] else 0}")
            print(f"First name is empty: {not user[1] or not user[1].strip()}")
            print(f"Last name is empty: {not user[2] or not user[2].strip()}")
        else:
            print("User not found")
            
        # Check all users with empty names
        cursor.execute('SELECT id, first_name, last_name, email FROM users WHERE first_name = "" OR last_name = "" OR first_name IS NULL OR last_name IS NULL')
        empty_name_users = cursor.fetchall()
        
        print(f"\nUsers with empty names: {len(empty_name_users)}")
        for user in empty_name_users:
            print(f"  ID: {user[0]}, First: '{user[1]}', Last: '{user[2]}', Email: {user[3]}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user_data()
