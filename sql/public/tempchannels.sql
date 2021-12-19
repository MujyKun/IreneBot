CREATE TABLE IF NOT EXISTS public.tempchannels
(
    chanellid bigint,
    delay integer,
    PRIMARY KEY (chanellid)
);

ALTER TABLE public.tempchannels
    OWNER to postgres;
COMMENT ON TABLE public.tempchannels
    IS 'A self-destruct channel that removes messages after t seconds.';