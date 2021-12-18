CREATE TABLE IF NOT EXISTS groupmembers.bloodtypes
(
    bloodid serial,
    name character(2)[],
    PRIMARY KEY (bloodid)
);

ALTER TABLE groupmembers.bloodtypes
    OWNER to postgres;
COMMENT ON TABLE groupmembers.bloodtypes
    IS 'A list of possible blood types.';