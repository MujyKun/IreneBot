CREATE TABLE IF NOT EXISTS public.languages
(
    languageid serial,
    shortname character(5)[],
    name text,
    PRIMARY KEY (languageid)
);

ALTER TABLE public.languages
    OWNER to postgres;
COMMENT ON TABLE public.languages
    IS 'The languages the bot has content for.';