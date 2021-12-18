CREATE TABLE IF NOT EXISTS interactions.interactiontypes
(
    typeid serial,
    name text,
    PRIMARY KEY (typeid)
);

ALTER TABLE interactions.interactiontypes
    OWNER to postgres;
COMMENT ON TABLE interactions.interactiontypes
    IS 'Types of Interactions';