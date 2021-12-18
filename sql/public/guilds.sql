CREATE TABLE IF NOT EXISTS public.guilds
(
    guildid bigint,
    PRIMARY KEY (guildid)
);

ALTER TABLE public.guilds
    OWNER to postgres;
COMMENT ON TABLE public.guilds
    IS 'Information about guilds that have been previously associated with the bot.';