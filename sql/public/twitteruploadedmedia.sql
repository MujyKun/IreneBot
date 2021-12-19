CREATE TABLE IF NOT EXISTS public.twitteruploadedmedia
(
    mediaid integer,
    twittermediaid bigint,
    PRIMARY KEY (mediaid)
);

ALTER TABLE public.twitteruploadedmedia
    OWNER to postgres;
COMMENT ON TABLE public.twitteruploadedmedia
    IS 'Media that has been uploaded to Twitter.';