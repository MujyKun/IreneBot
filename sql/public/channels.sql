CREATE TABLE IF NOT EXISTS public.channels
(
    channelid bigint,
    PRIMARY KEY (channelid)
);

ALTER TABLE public.channels
    OWNER to postgres;
COMMENT ON TABLE public.channels
    IS 'Manages the channels that have previously been associated with the bot.';