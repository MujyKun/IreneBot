CREATE TABLE IF NOT EXISTS unscramblegame.stats
(
    userid bigint,
    modeid integer,
    value integer,
    PRIMARY KEY (value)
);

ALTER TABLE unscramblegame.stats
    OWNER to postgres;
COMMENT ON TABLE unscramblegame.stats
    IS 'Stats a user has in every mode of the unscramble game.';