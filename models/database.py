import psycopg

class Database:
    def __init__(self, connection_string: str):
        # Initialize the database connection parameters
        self.connection_string = connection_string
        self.conn = None

    def connect(self):
        # Creates a new database connection if none exists
        if self.conn is None or self.conn.closed:
            try:
                self.conn = psycopg.connect(self.connection_string)
                return {"message": "the connection was established successfully!"}
            except Exception as e:
                return {"error": f"Error connecting to the database: {e}"}
        return self.conn
    
    def status(self):
        # Returns the status of the database connection
        if self.conn is None:
            return {"status": "No connection established."}
        elif self.conn.closed:
            return {"status": "Connection is closed."}
        else:
            return {"status": "Connection is open."}

    def close(self):
        # Closes the database connection if it exists
        if self.conn and not self.conn.closed:
            self.conn.close()
            return {"message": "the connection was closed successfully."}

    def execute(self, query, params=None, fetch=False):
        conn = self.conn if self.conn and not getattr(self.conn, "closed", True) else self.connect()
        if isinstance(conn, dict) and "error" in conn:
            return conn

        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if fetch and cur.description:
                    return cur.fetchall()
                conn.commit()
                return {"rowcount": cur.rowcount}
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            return {"error": f"Error executing query: {e}"}
