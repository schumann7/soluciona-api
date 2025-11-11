class User:
    def __init__ (self, id, username, email, phone, password, profile_picture, place_id, account_status, created_at):
        self.id = id # User ID
        self.username = username # Username
        self.email = email # Email
        self.phone = phone # Phone  
        self.password = password # Password
        self.profile_picture = profile_picture # Profile Picture
        self.place_id = place_id # Place ID
        self.account_status = account_status # Account Status
        self.created_at = created_at # Created At

def password_to_hash(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()