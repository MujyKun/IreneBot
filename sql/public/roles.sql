CREATE TABLE IF NOT EXISTS public.roles
(
    roleid bigint,
    typeids integer[],
    guildid bigint,
    PRIMARY KEY (roleid)
);

ALTER TABLE public.roles
    OWNER to postgres;
COMMENT ON TABLE public.roles
    IS 'Roles with a bot purpose.';