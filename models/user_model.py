class User:
    def __init__ (self, id, username, email, phone, password, account_type, city, campus, birthdate, created_at):
        self.id = id # User ID
        self.username = username # Username
        self.email = email # Email
        self.phone = phone # Phone  
        self.password = password # Password
        self.account_type = account_type # Account Type (Account level (admin, user, etc.), student or citizen)
        self.city = city # City
        self.campus = campus # Campus
        self.birthdate = birthdate # Birthdate
        self.created_at = created_at # Created At

def password_to_hash(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def convert_date(data_str: str) -> str:
    from datetime import datetime
    # Convert date from 'dd/mm/yyyy' to 'yyyy-mm-dd'
    try:
        data_formatada = datetime.strptime(data_str, "%d/%m/%Y").date()
        return data_formatada.isoformat()  # return 'YYYY-MM-DD'
    except ValueError:
        raise ValueError(f"Data inválida: '{data_str}'. Use o formato dd/mm/aaaa.")
