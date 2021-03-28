class Group:
    """A group of idols/celebrities"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('groupid')
        self.name = kwargs.get('groupname')
        self.debut_date = kwargs.get('debutdate')
        self.disband_date = kwargs.get('disbanddate')
        self.description = kwargs.get('description')
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
        self.members = []  # idol ids, not idol objects.
        self.fandom = kwargs.get('fandom')
        self.company = kwargs.get('company')
        self.website = kwargs.get('website')
        self.thumbnail = kwargs.get('thumbnail')
        self.banner = kwargs.get('banner')
        self.gender = kwargs.get('gender')
        self.skill = kwargs.get('skill')
        self.photo_count = 0
        self.tags = kwargs.get('tags')
        if self.tags:
            self.tags = self.tags.split(',')

