CREATE TABLE IF NOT EXISTS public.users
(
    userid bigint,
    sessionkey text,
    balance text,
    PRIMARY KEY (userid)
);

ALTER TABLE public.users
    OWNER to postgres;
COMMENT ON TABLE public.users IS 'User Information';