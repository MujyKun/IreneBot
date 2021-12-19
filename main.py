from discord import AutoShardedClient
from models import PgConnection


class Bot(AutoShardedClient):
    def __init__(self):
        super(Bot, self).__init__(...)


if __name__ == '__main__':
    # generate db
    db = PgConnection



    # migration
    #
    ...



