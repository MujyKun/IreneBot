CREATE TABLE IF NOT EXISTS blackjack.userstatus
(
    statusid serial,
    userid bigint,
    stand boolean,
    cards integer[],
    bid text,
    PRIMARY KEY (statusid, userid)
);

ALTER TABLE blackjack.userstatus
    OWNER to postgres;
COMMENT ON TABLE blackjack.userstatus
    IS 'The status of a user in a blackjack game.';