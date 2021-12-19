CREATE TABLE IF NOT EXISTS guessinggame.modes
(
    modeid serial,
    name text,
    PRIMARY KEY (modeid)
);

ALTER TABLE guessinggame.modes
    OWNER to postgres;
COMMENT ON TABLE guessinggame.modes
    IS 'The modes for the guessing game.';