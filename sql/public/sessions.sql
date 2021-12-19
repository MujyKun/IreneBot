CREATE TABLE IF NOT EXISTS public.sessions
(
    sessionid serial,
    used integer,
    sessiondate date,
    PRIMARY KEY (sessionid)
);

ALTER TABLE public.sessions
    OWNER to postgres;
COMMENT ON TABLE public.sessions
    IS 'A day by day session of the bot tracking command usage.';