CREATE TABLE IF NOT EXISTS public.statuses
(
    statusid serial,
    status text,
    PRIMARY KEY (statusid)
);

ALTER TABLE public.statuses
    OWNER to postgres;
COMMENT ON TABLE public.statuses
    IS 'The statuses the bot will iterate through.';