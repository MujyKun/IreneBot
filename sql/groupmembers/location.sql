CREATE TABLE IF NOT EXISTS groupmembers.location
(
    locationid serial,
    country text,
    city text,
    PRIMARY KEY (locationid)
);

ALTER TABLE groupmembers.location
    OWNER to postgres;
COMMENT ON TABLE groupmembers.location
    IS 'Contains a country and city. Useful to remove redundancy of repeated text, however is flawed in the sense that the city may not be known of a person.';