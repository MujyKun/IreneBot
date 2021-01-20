class Idol:
    """Represents an Idol/Celebrity."""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.full_name = kwargs.get('fullname')
        self.stage_name = kwargs.get('stagename')
        self.former_full_name = kwargs.get('formerfullname')
        self.former_stage_name = kwargs.get('formerstagename')
        self.birth_date = kwargs.get('birthdate')
        self.birth_country = kwargs.get('birthcountry')
        self.birth_city = kwargs.get('birthcity')
        self.gender = kwargs.get('gender')
        self.description = kwargs.get('description')
        self.height = kwargs.get('height')
        self.twitter = kwargs.get('twitter')
        self.youtube = kwargs.get('youtube')
        self.melon = kwargs.get('melon')
        self.instagram = kwargs.get('instagram')
        self.vlive = kwargs.get('vlive')
        self.spotify = kwargs.get('spotify')
        self.fancafe = kwargs.get('fancafe')
        self.facebook = kwargs.get('facebook')
        self.tiktok = kwargs.get('tiktok')
        self.aliases = []
        self.local_aliases = {}  # server_id: [aliases]
        self.groups = []
        self.zodiac = kwargs.get('zodiac')
        self.thumbnail = kwargs.get('thumbnail')
        self.banner = kwargs.get('banner')
        self.blood_type = kwargs.get('bloodtype')
        self.photo_count = 0
        # amount of times the idol has been called.
        self.called = 0
        self.tags = kwargs.get('tags')
        self.difficulty = kwargs.get('difficulty') or "medium"  # easy = 1, medium = 2, hard = 3
        if self.tags:
            self.tags = self.tags.split(',')
