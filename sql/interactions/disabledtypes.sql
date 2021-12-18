CREATE TABLE IF NOT EXISTS interactions.disabledtypes
(
    guildid bigint,
    interactionids integer[],
    PRIMARY KEY (guildid)
);

ALTER TABLE interactions.disabledtypes
    OWNER to postgres;
COMMENT ON TABLE interactions.disabledtypes
    IS 'The interaction types disabled for a guild';