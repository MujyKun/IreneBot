CREATE TABLE IF NOT EXISTS public.mods
(
    userid bigint,
    PRIMARY KEY (userid)
);

ALTER TABLE public.mods
    OWNER to postgres;
COMMENT ON TABLE public.mods IS 'General Moderators of the bot.';