from . import logger


class DbConnection:
    def __init__(self, db_host: str, db_name: str, db_user: str, db_pass: str, db_port: int):
        """
        Abstract version for a database connection.

        :param db_host: The database host to connect to.
        :param db_name: Database Name to connect to.
        :param db_user: Database User to log in as.
        :param db_pass: Password of the Database User.
        """
        self._db_host = db_host
        self._db_name = db_name
        self._db_user = db_user
        self._db_port = db_port
        self.__db_pass = db_pass
        self.__pool = None
        ...

    async def connect(self):
        """Connect to the PostgreSQL Database."""

        await self.__create_pool(**{
            "host": self._db_host,
            "database": self._db_name,
            "user": self._db_user,
            "password": self.__db_pass,
            "port": self._db_port
        })
        logger.debug(f"Connected to Database {self._db_name} as {self._db_user}.")
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

    async def fetch_row(self, query: str):
        """Fetch a row from a SQL query.

        :param query: (str) SQL Query to execute.
        """
        ...

    async def fetch(self, query: str):
        """Fetch rows from a SQL query.

        :param query: (str) SQL Query to execute.
        """
        ...

    async def generate(self):
        """Generate the database."""
        ...

    async def __create_pool(self, **login_payload):
        """Create and set the connection pool.

        :param login_payload: The login payload to pass into the concrete class.
        """
        ...
