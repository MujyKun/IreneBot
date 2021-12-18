CREATE TABLE IF NOT EXISTS groupmembers.person
(
    personid serial,
    dateid integer,
    nameid integer,
    formernameid integer,
    gender character(1)[],
    description text,
    height integer,
    displayid integer,
    socialid integer,
    locationid integer,
    tagid integer,
    bloodid integer,
    callcount integer,
    PRIMARY KEY (personid)
);

ALTER TABLE groupmembers.person
    OWNER to postgres;
COMMENT ON TABLE groupmembers.person
    IS 'A general person';