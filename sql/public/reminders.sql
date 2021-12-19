CREATE TABLE IF NOT EXISTS public.reminders
(
    id serial,
    userid bigint,
    reason text,
    dateid integer,
    PRIMARY KEY (id)
);

ALTER TABLE public.reminders
    OWNER to postgres;
COMMENT ON TABLE public.reminders
    IS 'All reminders that have or will be sent to a user.';