CREATE TABLE IF NOT EXISTS interactions.media
(
    url text,
    interactionid integer,
    PRIMARY KEY (url)
);

ALTER TABLE interactions.media
    OWNER to postgres;
COMMENT ON TABLE interactions.media
    IS 'Media URLs';