CREATE TABLE IF NOT EXISTS groupmembers.affiliation
(
    affiliationid serial,
    personid integer,
    groupid integer,
    positionids integer[],
    stagename text,
    PRIMARY KEY (affiliationid, personid, groupid)
);

ALTER TABLE groupmembers.affiliation
    OWNER to postgres;
COMMENT ON TABLE groupmembers.affiliation
    IS 'The affiliation of a person to a group.';