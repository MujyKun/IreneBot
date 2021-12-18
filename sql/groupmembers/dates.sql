CREATE TABLE IF NOT EXISTS groupmembers.dates
(
    dateid serial,
    startdate date,
    enddate date,
    PRIMARY KEY (dateid)
);

ALTER TABLE groupmembers.dates
    OWNER to postgres;
COMMENT ON TABLE groupmembers.dates
    IS 'Contains a start and end date.';