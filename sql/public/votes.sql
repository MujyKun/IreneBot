CREATE TABLE IF NOT EXISTS public.votes
(
    votedat timestamp without time zone,
    userid bigint,
    PRIMARY KEY (votedat, userid)
);

ALTER TABLE public.votes
    OWNER to postgres;