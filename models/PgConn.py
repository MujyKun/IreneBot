from . import DbConnection


class PgConnection(DbConnection):
    def __init__(self, *args):
        super(PgConnection, self).__init__(*args)

    async def connect(self):
        ...

    async def read_sql_file(self, file_name: str):
        ...

    async def execute(self, query: str):
        ...

    async def generate(self):
        ...