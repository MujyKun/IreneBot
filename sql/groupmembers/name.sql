CREATE TABLE IF NOT EXISTS groupmembers.name
(
    nameid serial,
    firstname text,
    lastname text,
    PRIMARY KEY (nameid)
);

ALTER TABLE groupmembers.name
    OWNER to postgres;
COMMENT ON TABLE groupmembers.name
    IS 'Contains a first and last name. Useful for people with several names. ';