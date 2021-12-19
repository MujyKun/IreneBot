import asyncpg
from . import DbConnection


class PgConnection(DbConnection):
    def __init__(self, *args, **kwargs):
        """
        Concrete version of a database connection using asyncpg.

        :param args: Params for DbConnection
        """
        self.pool = asyncpg.pool.Pool = None
        super(PgConnection, self).__init__(*args, **kwargs)

    async def read_sql_file(self, file_name: str):
        ...

    async def execute(self, query: str):
        ...

    async def fetch_row(self, query: str):
        ...

    async def fetch(self, query: str):
        ...

    async def generate(self):
        ...

    async def __create_pool(self, **login_payload):
        self.pool = await asyncpg.create_pool(**login_payload, command_timeout=60)
