CREATE TABLE IF NOT EXISTS public.logging
(
    guildid bigint,
    channelids bigint[],
    active boolean,
    sendall boolean,
    PRIMARY KEY (guildid)
);

ALTER TABLE public.logging
    OWNER to postgres;
COMMENT ON TABLE public.logging
    IS 'Guild Logging';