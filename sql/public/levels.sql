CREATE TABLE public.levels
(
    userid bigint,
    rob integer,
    daily integer,
    beg integer,
    profile integer,
    PRIMARY KEY (userid)
);

ALTER TABLE public.levels
    OWNER to postgres;
COMMENT ON TABLE public.levels
    IS 'The levels of a user.';