CREATE TABLE IF NOT EXISTS public.lastfm
(
    userid bigint,
    username text,
    PRIMARY KEY (userid)
);

ALTER TABLE public.lastfm
    OWNER to postgres;
COMMENT ON TABLE public.lastfm
    IS 'The LastFM usernames of a user.';