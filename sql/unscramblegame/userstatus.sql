CREATE TABLE IF NOT EXISTS unscramblegame.userstatus
(
    statusid serial,
    userid bigint,
    score integer,
    PRIMARY KEY (statusid, userid)
);

ALTER TABLE unscramblegame.userstatus
    OWNER to postgres;
COMMENT ON TABLE unscramblegame.userstatus
    IS 'The status of a user in an unscramble game.';