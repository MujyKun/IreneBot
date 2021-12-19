CREATE TABLE IF NOT EXISTS guessinggame.userstatus
(
    statusid serial,
    userid bigint,
    score integer,
    PRIMARY KEY (statusid, userid)
);

ALTER TABLE guessinggame.userstatus
    OWNER to postgres;
COMMENT ON TABLE guessinggame.userstatus
    IS 'The status of a user during a specific game.';