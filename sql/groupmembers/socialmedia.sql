CREATE TABLE IF NOT EXISTS groupmembers.socialmedia
(
    socialid serial,
    twitter text,
    youtube text,
    melon text,
    instagram text,
    vlive text,
    spotify text,
    fancafe text,
    facebook text,
    tiktok text,
    PRIMARY KEY (socialid)
);

ALTER TABLE groupmembers.socialmedia
    OWNER to postgres;
COMMENT ON TABLE groupmembers.socialmedia
    IS 'Contains information about social media. Will be linked to an entity. ';