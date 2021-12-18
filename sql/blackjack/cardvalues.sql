CREATE TABLE IF NOT EXISTS blackjack.cardvalues
(
    id serial,
    name text,
    value integer,
    PRIMARY KEY (id)
);

ALTER TABLE blackjack.cardvalues
    OWNER to postgres;
COMMENT ON TABLE blackjack.cardvalues
    IS 'The values of cards';