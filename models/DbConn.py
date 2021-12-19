
class DbConnection:
    def __init__(self, db_host, db_name, db_user, db_pass):
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