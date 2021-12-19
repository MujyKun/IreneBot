CREATE TABLE IF NOT EXISTS guessinggame.stats
(
    userid bigint,
    modeid integer,
    value integer,
    PRIMARY KEY (userid)
);

ALTER TABLE guessinggame.stats
    OWNER to postgres;
COMMENT ON TABLE guessinggame.stats
    IS 'Stats a user has in every mode of the guessing game.';