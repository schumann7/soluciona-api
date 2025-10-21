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

    def close(self):
        # Closes the database connection if it exists
        if self.conn and not self.conn.closed:
            self.conn.close()
            return {"message": "the connection was closed successfully."}

    def execute_query(self, query, params=None):
        # Executes a given SQL query with optional parameters
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if cur.description: # Check if the query returns data
                    result = cur.fetchall()
                    return result
                conn.commit()
        except Exception as e:
            conn.rollback()
            return {"error": f"Error executing query: {e}"}
        finally:
            self.close()