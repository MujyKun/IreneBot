CREATE TABLE IF NOT EXISTS blackjack.games
(
    gameid serial,
    channelid bigint,
    statusids integer[],
    active boolean,
    PRIMARY KEY (gameid)
);

ALTER TABLE blackjack.games
    OWNER to postgres;
COMMENT ON TABLE blackjack.games
    IS 'The active and inactive blackjack games.';