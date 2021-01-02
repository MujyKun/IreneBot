from Utility import resources as ex
from module import logger as log, exceptions
import re
import pytz
import parsedatetime
import locale
import datetime
import random


# noinspection PyBroadException,PyPep8
class Reminder:
    @staticmethod
    async def determine_time_type(user_input):
        """Determine if time is relative time or absolute time
        relative time: remind me to _____ in 6 days
        absolute time: remind me to _____ at 6PM"""
        # TODO: add "on", "tomorrow", and "tonight" as valid inputs

        in_index = user_input.rfind(" in ")
        at_index = user_input.rfind(" at ")
        if in_index == at_index:
            return None, None
        if in_index > at_index:
            return True, in_index
        return False, at_index

    @staticmethod
    async def process_reminder_reason(user_input, cutoff_index):
        """Return the reminder reason that comes before in/at"""
        user_input = user_input[0: cutoff_index]
        user_words = user_input.split()
        if user_words[0].lower() == "me":
            user_words.pop(0)
        if user_words[0].lower() == "to":
            user_words.pop(0)
        return " ".join(user_words)

    async def process_reminder_time(self, user_input, type_index, is_relative_time, user_id):
        """Return the datetime of the reminder depending on the time format"""
        remind_time = user_input[type_index + len(" in "): len(user_input)]

        if is_relative_time:
            if await self.process_relative_time_input(remind_time) > 2 * 3.154e7:  # 2 years in seconds
                raise ex.exceptions.TooLarge
            return datetime.datetime.now() + datetime.timedelta(
                seconds=await self.process_relative_time_input(remind_time))

        return await self.process_absolute_time_input(remind_time, user_id)

    @staticmethod
    async def process_relative_time_input(time_input):
        """Returns the relative time of the input in seconds"""
        year_aliases = ["years", "year", "yr", "y"]
        month_aliases = ["months", "month", "mo"]
        week_aliases = ["weeks", "week", "wk"]
        day_aliases = ["days", "day", "d"]
        hour_aliases = ["hours", "hour", "hrs", "hr", "h"]
        minute_aliases = ["minutes", "minute", "mins", "min", "m"]
        second_aliases = ["seconds", "second", "secs", "sec", "s"]
        time_units = [[year_aliases, 31536000], [month_aliases, 2592000], [week_aliases, 604800], [day_aliases, 86400],
                      [hour_aliases, 3600], [minute_aliases, 60], [second_aliases, 1]]

        remind_time = 0  # in seconds
        input_elements = re.findall(r"[^\W\d_]+|\d+", time_input)

        all_aliases = [alias for time_unit in time_units for alias in time_unit[0]]
        if not any(alias in input_elements for alias in all_aliases):
            raise exceptions.ImproperFormat

        for time_element in input_elements:
            try:
                int(time_element)
            except:
                # purposefully creating an error to locate which elements are words vs integers.
                for time_unit in time_units:
                    if time_element in time_unit[0]:
                        remind_time += time_unit[1] * int(input_elements[input_elements.index(time_element) - 1])
        return remind_time

    async def process_absolute_time_input(self, time_input, user_id):
        """Returns the absolute date time of the input"""
        user_timezone = await self.get_user_timezone(user_id)
        if not user_timezone:
            raise ex.exceptions.NoTimeZone
        cal = parsedatetime.Calendar()
        try:
            datetime_obj, _ = cal.parseDT(datetimeString=time_input, tzinfo=pytz.timezone(user_timezone))
            reminder_datetime = datetime_obj.astimezone(pytz.utc)
            return reminder_datetime
        except:
            raise ex.exceptions.ImproperFormat

    @staticmethod
    async def get_user_timezone(user_id):
        """Returns the user's timezone"""
        return ex.cache.timezones.get(user_id)

    @staticmethod
    async def set_user_timezone(user_id, timezone):
        """Set user timezone"""
        user_timezone = ex.cache.timezones.get(user_id)
        ex.cache.timezones[user_id] = timezone
        if user_timezone:
            await ex.conn.execute("UPDATE reminders.timezones SET timezone = $1 WHERE userid = $2", timezone, user_id)
        else:
            await ex.conn.execute("INSERT INTO reminders.timezones(userid, timezone) VALUES ($1, $2)", user_id,
                                  timezone)

    @staticmethod
    async def remove_user_timezone(user_id):
        """Remove user timezone"""
        try:
            ex.cache.timezones.pop(user_id)
            await ex.conn.execute("DELETE FROM reminders.timezones WHERE userid = $1", user_id)
        except:
            pass

    @staticmethod
    async def process_timezone_input(input_timezone, input_country_code=None):
        """Convert timezone abbreviation and country code to standard timezone name"""

        def now_tz_str(time_zone):
            return datetime.datetime.now(pytz.timezone(time_zone)).strftime("%Z")

        try:
            input_timezone = input_timezone.upper()
            input_country_code = input_country_code.upper()
        except:
            pass

        # Format if user input is in GMT offset format
        if any(char.isdigit() for char in input_timezone):
            try:
                timezone_offset = (re.findall(r"[+-]\d+", input_timezone))[0]
                utc_offset = f"-{timezone_offset[1:len(timezone_offset)]}" \
                                if timezone_offset[0] == "+" else f"+{timezone_offset[1:len(timezone_offset)]}"
                input_timezone = 'Etc/GMT' + utc_offset
            except:
                pass

        matching_timezones = None

        try:
            matching_timezones = set(common_tz for common_tz in pytz.common_timezones
                                     if now_tz_str(common_tz) == now_tz_str(input_timezone))
        except pytz.exceptions.UnknownTimeZoneError:
            matching_timezones = set(common_tz for common_tz in pytz.common_timezones
                                     if now_tz_str(common_tz) == input_timezone)
        except:
            pass

        # Find the timezones which share both same timezone input and the same country code
        if input_country_code:
            try:
                country_timezones = set(pytz.country_timezones[input_country_code])
                possible_timezones = matching_timezones.intersection(country_timezones)
            except:
                possible_timezones = matching_timezones
        else:
            possible_timezones = matching_timezones

        if not possible_timezones:
            return None

        return random.choice(list(possible_timezones))

    @staticmethod
    async def get_locale_time(m_time, user_timezone=None):
        """ Return a string containing locale date format. For now, enforce all weekdays to be en_US format"""
        # Set locale to server locale
        time_format = '%I:%M:%S%p %Z'
        locale.setlocale(locale.LC_ALL, '')

        if not user_timezone:
            return m_time.strftime('%a %x %I:%M:%S%p %Z')

        # Use weekday format of server
        weekday = m_time.strftime('%a')

        simplified_user_timezone = f"{(ex.cache.locale_by_timezone[user_timezone].replace('-', '_'))}.utf8"
        locale.setlocale(locale.LC_ALL, simplified_user_timezone)  # Set to user locale
        locale_date = m_time.astimezone(pytz.timezone(user_timezone)).strftime('%x')
        locale.setlocale(locale.LC_ALL, '')  # Reset locale back to server locale

        local_time = m_time.astimezone(pytz.timezone(user_timezone))
        local_time = local_time.strftime(time_format)
        return f"{weekday} {locale_date} {local_time}"

    @staticmethod
    async def set_reminder(remind_reason, remind_time, user_id):
        """Add reminder date to cache and db."""
        await ex.conn.execute("INSERT INTO reminders.reminders(userid, reason, timestamp) VALUES ($1, $2, $3)",
                              user_id, remind_reason, remind_time)
        remind_id = ex.first_result(await ex.conn.fetchrow(
            "SELECT id FROM reminders.reminders WHERE userid=$1 AND reason=$2 AND timestamp=$3 ORDER BY id DESC",
            user_id, remind_reason, remind_time))
        user_reminders = ex.cache.reminders.get(user_id)
        remind_info = [remind_id, remind_reason, remind_time]
        if user_reminders:
            user_reminders.append(remind_info)
        else:
            ex.cache.reminders[user_id] = [remind_info]

    @staticmethod
    async def get_reminders(user_id):
        """Get the reminders of a user"""
        return ex.cache.reminders.get(user_id)

    @staticmethod
    async def remove_user_reminder(user_id, reminder_id):
        """Remove a reminder from the cache and the database."""
        try:
            # remove from cache
            reminders = ex.cache.reminders.get(user_id)
            if reminders:
                for reminder in reminders:
                    current_reminder_id = reminder[0]
                    if current_reminder_id == reminder_id:
                        reminders.remove(reminder)
        except Exception as e:
            log.console(e)
        await ex.conn.execute("DELETE FROM reminders.reminders WHERE id = $1", reminder_id)

    @staticmethod
    async def get_all_reminders_from_db():
        """Get all reminders from the db (all users)"""
        return await ex.conn.fetch("SELECT id, userid, reason, timestamp FROM reminders.reminders")

    @staticmethod
    async def get_all_timezones_from_db():
        """Get all timezones from the db (all users)"""
        return await ex.conn.fetch("SELECT userid, timezone FROM reminders.timezones")
