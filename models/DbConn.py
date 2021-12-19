
class DbConnection:
    def __init__(self, db_host: str, db_name: str, db_user: str, db_pass: str):
        """
        Abstract version for a database connection.

        :param db_host: The database host to connect to.
        :param db_name: Database Name to connect to.
        :param db_user: Database User to log in as.
        :param db_pass: Password of the Database User.
        """
        ...

    async def connect(self):
        """Create  a pool to the PostgreSQL DB."""
        ...

    async def read_sql_file(self, file_name: str):
        """Read a SQL file.

        :param file_name: str File name to read.
        """
        ...

    async def execute(self, query: str):
        """Execute a SQL query.

        :param query: (str) SQL Query to execute.
        """
        ...

    async def generate(self):
        """Generate the database."""
        ...