from controllers.db_instance import db

DDL_STATEMENTS = [
    # places must exist first
    """
    CREATE TABLE IF NOT EXISTS places (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        type VARCHAR(100) NOT NULL
    );
    """,

    # users: place_id column will be added/kept; account_type and birthdate removed
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        phone VARCHAR(20),
        password VARCHAR(255) NOT NULL,
        profile_picture INT,
        place_id INTEGER,
        account_status VARCHAR(8) NOT NULL DEFAULT 'active' CHECK (account_status IN ('active', 'inactive')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # reports: create before images because images references reports
    """
    CREATE TABLE IF NOT EXISTS reports (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        latitude DOUBLE PRECISION NOT NULL,
        longitude DOUBLE PRECISION NOT NULL,
        description TEXT,
        place_id INTEGER NOT NULL,
        address VARCHAR(255),
        status VARCHAR(8) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
        registered_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
        registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # images: now safe to reference reports(id)
    """
    CREATE TABLE IF NOT EXISTS images (
        id SERIAL PRIMARY KEY,
        url_storage VARCHAR(1024) NOT NULL,
        report_id INTEGER REFERENCES reports(id) ON DELETE CASCADE,
        image_type VARCHAR(50),
        image_size BIGINT,
        registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # add FK users.profile_picture -> images.id (images now exists)
    """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = 'users' AND tc.constraint_type = 'FOREIGN KEY' AND kcu.column_name = 'profile_picture'
      ) THEN
        ALTER TABLE users
        ADD CONSTRAINT fk_profile_picture
        FOREIGN KEY (profile_picture)
        REFERENCES images(id)
        ON DELETE SET NULL;
      END IF;
    END$$;
    """,

    # ensure place_id exists on users and reports
    """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='place_id'
      ) THEN
        ALTER TABLE users ADD COLUMN place_id INTEGER;
      END IF;
      IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='reports' AND column_name='place_id'
      ) THEN
        ALTER TABLE reports ADD COLUMN place_id INTEGER;
      END IF;
    END$$;
    """,

    # add FK users.place_id -> places(id)
    """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = 'users' AND tc.constraint_type = 'FOREIGN KEY' AND kcu.column_name = 'place_id'
      ) THEN
        ALTER TABLE users
        ADD CONSTRAINT fk_users_place_id
        FOREIGN KEY (place_id)
        REFERENCES places(id)
        ON DELETE SET NULL;
      END IF;
    END$$;
    """,

    # add FK reports.place_id -> places(id) with ON DELETE CASCADE (delete reports when place deleted)
    """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = 'reports' AND tc.constraint_type = 'FOREIGN KEY' AND kcu.column_name = 'place_id'
      ) THEN
        ALTER TABLE reports
        ADD CONSTRAINT fk_reports_place_id
        FOREIGN KEY (place_id)
        REFERENCES places(id)
        ON DELETE CASCADE;
      END IF;
    END$$;
    """
]

def create_tables():
    for i, sql in enumerate(DDL_STATEMENTS, start=1):
        res = db.execute(sql)
        if isinstance(res, dict) and res.get("error"):
            print(f"[seeder] statement {i} failed: {res.get('error')}")
        else:
            print(f"[seeder] statement {i} executed successfully.")
    print("[seeder] finished.")

if __name__ == "__main__":
    create_tables()