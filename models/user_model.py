class User:
    def __init__ (self, id, username, email, phone, password, account_type, city, campus, created_at):
        self.id = id # User ID
        self.username = username # Username
        self.email = email # Email
        self.phone = phone # Phone  
        self.password = password # Password
        self.account_type = account_type # Account Type (Account level (admin, user, etc.), student or citizen)
        self.city = city # City
        self.campus = campus # Campus
        self.created_at = created_at # Created At

    def password_to_hash(self, password):
        # Implement password hashing logic here
        pass