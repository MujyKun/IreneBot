CREATE TABLE IF NOT EXISTS public.selfassignroles
(
    roleid bigint,
    channelid bigint,
    name text,
    PRIMARY KEY (roleid)
);

ALTER TABLE public.selfassignroles
    OWNER to postgres;
COMMENT ON TABLE public.selfassignroles
    IS 'Roles that can be self assigned in a channel.';