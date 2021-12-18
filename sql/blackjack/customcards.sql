CREATE TABLE IF NOT EXISTS blackjack.customcards
(
    id serial,
    valueid integer,
    personid integer,
    filename text,
    PRIMARY KEY (id)
);

ALTER TABLE blackjack.customcards
    OWNER to postgres;
COMMENT ON TABLE blackjack.customcards
    IS 'Custom playing cards with unique backgrounds.';