CREATE TABLE IF NOT EXISTS groupmembers.company
(
    companyid serial,
    name text,
    description text,
    dateid integer,
    PRIMARY KEY (companyid)
);

ALTER TABLE groupmembers.company
    OWNER to postgres;
COMMENT ON TABLE groupmembers.company
    IS 'An enterprise.';