CREATE TABLE IF NOT EXISTS groupmembers."position"
(
    positionid serial,
    name text,
    PRIMARY KEY (positionid)
);

ALTER TABLE groupmembers."position"
    OWNER to postgres;
COMMENT ON TABLE groupmembers."position"
    IS 'A position such as vocal, leader, dancer.';