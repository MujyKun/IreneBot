CREATE TABLE IF NOT EXISTS public.commandusage
(
    sessionid integer,
    commandname text,
    count integer,
    PRIMARY KEY (sessionid, commandname)
);

ALTER TABLE public.commandusage
    OWNER to postgres;
COMMENT ON TABLE public.commandusage
    IS 'The usage of every command during a session.';