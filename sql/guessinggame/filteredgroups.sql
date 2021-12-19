CREATE TABLE IF NOT EXISTS guessinggame.filteredgroups
(
    userid bigint,
    groupids integer[],
    PRIMARY KEY (userid)
);

ALTER TABLE guessinggame.filteredgroups
    OWNER to postgres;
COMMENT ON TABLE guessinggame.filteredgroups
    IS 'The groups a user has filtered to show in the guessing game.';