CREATE TABLE IF NOT EXISTS groupmembers.automedia
(
    channelid bigint,
    personids integer[],
    PRIMARY KEY (channelid)
);

ALTER TABLE groupmembers.automedia
    OWNER to postgres;
COMMENT ON TABLE groupmembers.automedia
    IS 'Automatically post a list of person ids in a channel.';