CREATE TABLE IF NOT EXISTS public.guildprefixes
(
    guildid bigint,
    prefix text,
    PRIMARY KEY (guildid)
);

ALTER TABLE public.guildprefixes
    OWNER to postgres;
COMMENT ON TABLE public.guildprefixes
    IS 'The custom prefixes for a guild.';