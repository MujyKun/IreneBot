CREATE TABLE IF NOT EXISTS public.apiusage
(
    key text,
    endpoint text,
    count integer,
    PRIMARY KEY (key, endpoint)
);

ALTER TABLE public.apiusage
    OWNER to postgres;
COMMENT ON TABLE public.apiusage
    IS 'The usage for the bot''s API.';