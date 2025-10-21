from app import db

def create_tables():
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        phone VARCHAR(20),
        password VARCHAR(255) NOT NULL,
        account_type JSONB NOT NULL,
        city VARCHAR(100),
        campus VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
    db.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            description TEXT,
            place VARCHAR(255),
            registered_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
            registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print ("Tables created successfully or table already exists.")

create_tables()