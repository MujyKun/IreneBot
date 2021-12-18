CREATE TABLE IF NOT EXISTS public.customcommands
(
    commandid serial,
    guildid bigint,
    name text,
    content text,
    PRIMARY KEY (commandid)
);

ALTER TABLE public.customcommands
    OWNER to postgres;
COMMENT ON TABLE public.customcommands
    IS 'Custom commands for a guild.';