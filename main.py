from discord import AutoShardedClient


class Bot(AutoShardedClient):
    def __init__(self):
        super(Bot, self).__init__(...)


if __name__ == '__main__':
    ...
