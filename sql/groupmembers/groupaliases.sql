CREATE TABLE IF NOT EXISTS groupmembers.groupaliases
(
    aliasid serial,
    alias text,
    groupid integer,
    guildid bigint,
    PRIMARY KEY (aliasid)
);

ALTER TABLE groupmembers.groupaliases
    OWNER to postgres;
COMMENT ON TABLE groupmembers.groupaliases
    IS 'The aliases of a group.';