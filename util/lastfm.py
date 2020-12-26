from Utility import resources as ex
from module.keys import last_fm_api_key, last_fm_root_url, last_fm_headers
from module import logger as log


class LastFM:
    @staticmethod
    def create_fm_payload(method, user=None, limit=None, time_period=None):
        """Creates the payload to be sent to Last FM"""
        payload = {
            'api_key': last_fm_api_key,
            'method': method,
            'format': 'json'
        }
        if user:
            payload['user'] = user
        if limit:
            payload['limit'] = limit
        if time_period:
            payload['period'] = time_period
        return payload

    async def get_fm_response(self, method, user=None, limit=None, time_period=None):
        """Receives the response from Last FM"""
        async with self.session.get(last_fm_root_url, headers=last_fm_headers, params=self.create_fm_payload(method, user, limit, time_period)) as response:
            return await response.json()

    async def get_fm_username(self, user_id):
        """Gets Last FM username from the DB."""
        return self.first_result(await self.conn.fetchrow("SELECT username FROM lastfm.users WHERE userid = $1", user_id))

    async def set_fm_username(self, user_id, username):
        """Sets Last FM username to the DB."""
        try:
            if not await self.get_fm_username(user_id):
                await self.conn.execute("INSERT INTO lastfm.users(userid, username) VALUES ($1, $2)", user_id, username)
            else:
                await self.conn.execute("UPDATE lastfm.users SET username = $1 WHERE userid = $2", username, user_id)
            return True
        except Exception as e:
            log.console(e)
            return e
