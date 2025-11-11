import psycopg

class Database:
    def __init__(self, connection_string: str):
        # Initialize the database connection parameters
        self.connection_string = connection_string
        self.conn = None

    def connect(self):
        # Creates a new database connection if none exists
        if self.conn is None or getattr(self.conn, "closed", True):
            try:
                self.conn = psycopg.connect(self.connection_string)
                # return the actual connection on success
                return self.conn
            except Exception as e:
                return {"error": f"Error connecting to the database: {e}"}
        return self.conn
    
    def status(self):
        # Returns the status of the database connection
        if self.conn is None:
            return {"status": "No connection established."}
        elif getattr(self.conn, "closed", True):
            return {"status": "Connection is closed."}
        else:
            return {"status": "Connection is open."}

    def close(self):
        # Closes the database connection if it exists
        if self.conn and not getattr(self.conn, "closed", True):
            self.conn.close()
            return {"message": "the connection was closed successfully."}

    def execute(self, query, params=None):
        conn = self.conn if self.conn and not getattr(self.conn, "closed", True) else self.connect()
        if isinstance(conn, dict) and "error" in conn:
            return conn

        try:
            with conn.cursor() as cur:
                cur.execute(query, params)

                if cur.description:
                    # fetch returned rows
                    result = cur.fetchall()
                    # commit so the INSERT/UPDATE is persisted
                    conn.commit()
                    return result

                conn.commit()
                return {"message": "Query executed successfully."}

        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            return {"error": f"Error executing query: {e}"}