CREATE TABLE IF NOT EXISTS unscramblegame.games
(
    gameid serial,
    dateid integer,
    statusids integer[],
    modeid integer,
    PRIMARY KEY (gameid)
);

ALTER TABLE unscramblegame.games
    OWNER to postgres;
COMMENT ON TABLE unscramblegame.games
    IS 'Information about an unscramble game.';