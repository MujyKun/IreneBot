CREATE TABLE IF NOT EXISTS public.twitterfollowage
(
    username text,
    channelid bigint,
    roleid bigint,
    PRIMARY KEY (username, channelid)
);

ALTER TABLE public.twitterfollowage
    OWNER to postgres;
COMMENT ON TABLE public.twitterfollowage
    IS 'The discord text channels that are following a twitter user.';