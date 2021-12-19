CREATE TABLE IF NOT EXISTS public.guilds
(
    guildid bigint,
    name text,
    emojicount integer,
    region text,
    afktimeout integer,
    icon text,
    ownerid bigint,
    banner text,
    description text,
    mfalevel integer,
    splash text,
    nitrolevel integer,
    boosts integer,
    textchannelcount integer,
    voicechannelcount integer,
    categorycount integer,
    emojilimit integer,
    membercount integer,
    rolecount integer,
    shardid integer,
    createdate timestamp with time zone,
	hasbot boolean,
    PRIMARY KEY (guildid)
);

ALTER TABLE public.guilds
    OWNER to postgres;
COMMENT ON TABLE public.guilds
    IS 'Information about guilds that have been previously associated with the bot.';