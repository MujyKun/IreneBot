CREATE TABLE IF NOT EXISTS groupmembers.display
(
    displayid serial,
    avatar text,
    banner text,
    PRIMARY KEY (displayid)
);

ALTER TABLE groupmembers.display
    OWNER to postgres;
COMMENT ON TABLE groupmembers.display
    IS 'Contains the URL to an avatar and banner';