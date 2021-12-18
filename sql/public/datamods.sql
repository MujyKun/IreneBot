CREATE TABLE IF NOT EXISTS public.datamods
(
    userid bigint,
    PRIMARY KEY (userid)
);

ALTER TABLE public.datamods
    OWNER to postgres;
COMMENT ON TABLE public.datamods IS 'Data moderators of the bot.';