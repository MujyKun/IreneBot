CREATE TABLE IF NOT EXISTS public.botbanned
(
    userid bigint,
    PRIMARY KEY (userid)
);

ALTER TABLE public.botbanned
    OWNER to postgres;
COMMENT ON TABLE public.botbanned IS 'Users that are currently banned from the bot.';