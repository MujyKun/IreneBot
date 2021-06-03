SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;
CREATE SCHEMA archive;
ALTER SCHEMA archive OWNER TO postgres;
CREATE SCHEMA biasgame;
ALTER SCHEMA biasgame OWNER TO postgres;
CREATE SCHEMA blackjack;
ALTER SCHEMA blackjack OWNER TO postgres;
CREATE SCHEMA currency;
ALTER SCHEMA currency OWNER TO postgres;
CREATE SCHEMA dreamcatcher;
ALTER SCHEMA dreamcatcher OWNER TO postgres;
CREATE SCHEMA general;
ALTER SCHEMA general OWNER TO postgres;
CREATE SCHEMA gg;
ALTER SCHEMA gg OWNER TO postgres;
CREATE SCHEMA groupmembers;
ALTER SCHEMA groupmembers OWNER TO postgres;
CREATE SCHEMA kiyomi;
ALTER SCHEMA kiyomi OWNER TO postgres;
CREATE SCHEMA lastfm;
ALTER SCHEMA lastfm OWNER TO postgres;
CREATE SCHEMA logging;
ALTER SCHEMA logging OWNER TO postgres;
CREATE SCHEMA patreon;
ALTER SCHEMA patreon OWNER TO postgres;
CREATE SCHEMA pgagent;
ALTER SCHEMA pgagent OWNER TO postgres;
COMMENT ON SCHEMA pgagent IS 'pgAgent system tables';
CREATE SCHEMA reminders;
ALTER SCHEMA reminders OWNER TO postgres;
CREATE SCHEMA selfassignroles;
ALTER SCHEMA selfassignroles OWNER TO postgres;
CREATE SCHEMA stats;
ALTER SCHEMA stats OWNER TO postgres;
CREATE SCHEMA testdb;
ALTER SCHEMA testdb OWNER TO postgres;
CREATE SCHEMA twitch;
ALTER SCHEMA twitch OWNER TO postgres;
CREATE SCHEMA weverse;
ALTER SCHEMA weverse OWNER TO postgres;
CREATE SCHEMA youtube;
ALTER SCHEMA youtube OWNER TO postgres;
CREATE EXTENSION IF NOT EXISTS adminpack WITH SCHEMA pg_catalog;
COMMENT ON EXTENSION adminpack IS 'administrative functions for PostgreSQL';
SET default_tablespace = '';
SET default_table_access_method = heap;
CREATE TABLE archive.archivedchannels (
    filename text,
    filetype text,
    folderid text,
    channelid bigint,
    id integer NOT NULL
);
ALTER TABLE archive.archivedchannels OWNER TO postgres;
CREATE SEQUENCE archive.archivedchannels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE archive.archivedchannels_id_seq OWNER TO postgres;
ALTER SEQUENCE archive.archivedchannels_id_seq OWNED BY archive.archivedchannels.id;
CREATE TABLE archive.channellist (
    channelid bigint,
    guildid bigint,
    driveid text,
    name text,
    id integer NOT NULL
);
ALTER TABLE archive.channellist OWNER TO postgres;
CREATE SEQUENCE archive.channellist_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE archive.channellist_id_seq OWNER TO postgres;
ALTER SEQUENCE archive.channellist_id_seq OWNED BY archive.channellist.id;
CREATE TABLE archive.driveids (
    linkid text,
    name text,
    id integer NOT NULL
);
ALTER TABLE archive.driveids OWNER TO postgres;
CREATE SEQUENCE archive.driveids_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE archive.driveids_id_seq OWNER TO postgres;
ALTER SEQUENCE archive.driveids_id_seq OWNED BY archive.driveids.id;
CREATE TABLE biasgame.winners (
    id integer NOT NULL,
    idolid integer,
    userid bigint,
    wins integer
);
ALTER TABLE biasgame.winners OWNER TO postgres;
CREATE SEQUENCE biasgame.winners_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE biasgame.winners_id_seq OWNER TO postgres;
ALTER SEQUENCE biasgame.winners_id_seq OWNED BY biasgame.winners.id;
CREATE TABLE blackjack.cardvalues (
    id integer NOT NULL,
    name text NOT NULL,
    value integer
);
ALTER TABLE blackjack.cardvalues OWNER TO postgres;
CREATE SEQUENCE blackjack.cards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE blackjack.cards_id_seq OWNER TO postgres;
ALTER SEQUENCE blackjack.cards_id_seq OWNED BY blackjack.cardvalues.id;
CREATE TABLE blackjack.currentstatus (
    userid bigint NOT NULL,
    stand integer,
    inhand text,
    total integer,
    acesused text
);
ALTER TABLE blackjack.currentstatus OWNER TO postgres;
CREATE TABLE blackjack.games (
    gameid integer NOT NULL,
    player1 bigint,
    player2 bigint,
    bid1 text,
    bid2 text,
    channelid bigint
);
ALTER TABLE blackjack.games OWNER TO postgres;
CREATE SEQUENCE blackjack.games_gameid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE blackjack.games_gameid_seq OWNER TO postgres;
ALTER SEQUENCE blackjack.games_gameid_seq OWNED BY blackjack.games.gameid;
CREATE TABLE blackjack.playingcards (
    id integer NOT NULL,
    cardvalueid integer,
    bgidolid integer,
    filename text
);
ALTER TABLE blackjack.playingcards OWNER TO postgres;
CREATE SEQUENCE blackjack.playingcards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE blackjack.playingcards_id_seq OWNER TO postgres;
ALTER SEQUENCE blackjack.playingcards_id_seq OWNED BY blackjack.playingcards.id;
CREATE TABLE currency.blackjack (
    gameid integer NOT NULL,
    cardid integer,
    "position" integer
);
ALTER TABLE currency.blackjack OWNER TO postgres;
CREATE TABLE currency.cardvalues (
    cardname text,
    value integer,
    cardid integer NOT NULL
);
ALTER TABLE currency.cardvalues OWNER TO postgres;
CREATE SEQUENCE currency.cardvalues_cardid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE currency.cardvalues_cardid_seq OWNER TO postgres;
ALTER SEQUENCE currency.cardvalues_cardid_seq OWNED BY currency.cardvalues.cardid;
CREATE TABLE currency.currency (
    userid bigint NOT NULL,
    money text
);
ALTER TABLE currency.currency OWNER TO postgres;
CREATE TABLE currency.games (
    player1 bigint,
    player2 bigint,
    bid1 integer,
    bid2 integer,
    score1 integer,
    score2 integer,
    type text,
    stand integer,
    gameid integer NOT NULL
);
ALTER TABLE currency.games OWNER TO postgres;
CREATE SEQUENCE currency.games_gameid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE currency.games_gameid_seq OWNER TO postgres;
ALTER SEQUENCE currency.games_gameid_seq OWNED BY currency.games.gameid;
CREATE TABLE currency.levels (
    userid bigint NOT NULL,
    rob integer,
    daily integer,
    beg integer,
    profile integer,
    profilexp integer
);
ALTER TABLE currency.levels OWNER TO postgres;
CREATE TABLE currency.logging (
    channelid text NOT NULL
);
ALTER TABLE currency.logging OWNER TO postgres;
CREATE TABLE currency.loggingprivate (
    channelid text NOT NULL
);
ALTER TABLE currency.loggingprivate OWNER TO postgres;
CREATE TABLE currency.raffle (
    raffleid integer NOT NULL,
    winner integer,
    amount integer,
    finished integer
);
ALTER TABLE currency.raffle OWNER TO postgres;
CREATE TABLE currency.raffledata (
    raffleid integer NOT NULL,
    userid text,
    amount integer
);
ALTER TABLE currency.raffledata OWNER TO postgres;
CREATE TABLE currency.valueplaces (
    name text,
    length integer,
    length2 integer,
    length3 integer
);
ALTER TABLE currency.valueplaces OWNER TO postgres;
CREATE TABLE dreamcatcher.dchdlinks (
    link text,
    member text,
    postnumber integer,
    id integer NOT NULL
);
ALTER TABLE dreamcatcher.dchdlinks OWNER TO postgres;
CREATE SEQUENCE dreamcatcher.dchdlinks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE dreamcatcher.dchdlinks_id_seq OWNER TO postgres;
ALTER SEQUENCE dreamcatcher.dchdlinks_id_seq OWNED BY dreamcatcher.dchdlinks.id;
CREATE TABLE dreamcatcher.dcpost (
    postid integer NOT NULL
);
ALTER TABLE dreamcatcher.dcpost OWNER TO postgres;
CREATE TABLE dreamcatcher.dcurl (
    url text NOT NULL,
    member text NOT NULL
);
ALTER TABLE dreamcatcher.dcurl OWNER TO postgres;
CREATE TABLE dreamcatcher.dreamcatcher (
    channelid bigint NOT NULL,
    roleid bigint
);
ALTER TABLE dreamcatcher.dreamcatcher OWNER TO postgres;
CREATE TABLE general.blacklisted (
    userid bigint NOT NULL
);
ALTER TABLE general.blacklisted OWNER TO postgres;
CREATE TABLE general.botstatus (
    id integer NOT NULL,
    status text
);
ALTER TABLE general.botstatus OWNER TO postgres;
CREATE SEQUENCE general.botstatus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE general.botstatus_id_seq OWNER TO postgres;
ALTER SEQUENCE general.botstatus_id_seq OWNED BY general.botstatus.id;
CREATE TABLE general.customcommands (
    id integer NOT NULL,
    serverid bigint,
    commandname text,
    message text
);
ALTER TABLE general.customcommands OWNER TO postgres;
CREATE SEQUENCE general.customcommands_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE general.customcommands_id_seq OWNER TO postgres;
ALTER SEQUENCE general.customcommands_id_seq OWNED BY general.customcommands.id;
CREATE TABLE general.disabledinteractions (
    serverid bigint NOT NULL,
    interactions text
);
ALTER TABLE general.disabledinteractions OWNER TO postgres;
CREATE TABLE general.gamesdisabled (
    channelid bigint NOT NULL
);
ALTER TABLE general.gamesdisabled OWNER TO postgres;
COMMENT ON TABLE general.gamesdisabled IS 'List of channels with games disabled';
CREATE TABLE general.interactions (
    url text NOT NULL,
    interaction text
);
ALTER TABLE general.interactions OWNER TO postgres;
CREATE TABLE general.languages (
    userid bigint NOT NULL,
    language text
);
ALTER TABLE general.languages OWNER TO postgres;
CREATE TABLE general.lastvoted (
    userid bigint NOT NULL,
    votetimestamp timestamp with time zone DEFAULT now()
);
ALTER TABLE general.lastvoted OWNER TO postgres;
CREATE TABLE general.modmail (
    userid bigint NOT NULL,
    channelid bigint NOT NULL
);
ALTER TABLE general.modmail OWNER TO postgres;
CREATE TABLE general.muteroles (
    roleid bigint NOT NULL
);
ALTER TABLE general.muteroles OWNER TO postgres;
CREATE TABLE general.notifications (
    id integer NOT NULL,
    guildid bigint,
    userid bigint,
    phrase text
);
ALTER TABLE general.notifications OWNER TO postgres;
CREATE SEQUENCE general.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE general.notifications_id_seq OWNER TO postgres;
ALTER SEQUENCE general.notifications_id_seq OWNED BY general.notifications.id;
CREATE TABLE general.nword (
    userid bigint NOT NULL,
    nword integer
);
ALTER TABLE general.nword OWNER TO postgres;
CREATE TABLE general.serverprefix (
    serverid bigint NOT NULL,
    prefix text
);
ALTER TABLE general.serverprefix OWNER TO postgres;
CREATE TABLE general.tempchannels (
    chanid bigint NOT NULL,
    delay bigint
);
ALTER TABLE general.tempchannels OWNER TO postgres;
CREATE TABLE general.welcome (
    channelid bigint,
    serverid bigint NOT NULL,
    message text,
    enabled integer
);
ALTER TABLE general.welcome OWNER TO postgres;
COMMENT ON TABLE general.welcome IS 'Welcome Messages ';
CREATE TABLE general.welcomeroles (
    guildid bigint NOT NULL,
    roleid bigint
);
ALTER TABLE general.welcomeroles OWNER TO postgres;
CREATE TABLE gg.filteredgroups (
    id integer NOT NULL,
    userid bigint,
    groupid integer
);
ALTER TABLE gg.filteredgroups OWNER TO postgres;
CREATE SEQUENCE gg.filteredgroups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE gg.filteredgroups_id_seq OWNER TO postgres;
ALTER SEQUENCE gg.filteredgroups_id_seq OWNED BY gg.filteredgroups.id;
CREATE TABLE gg.filterenabled (
    userid bigint NOT NULL
);
ALTER TABLE gg.filterenabled OWNER TO postgres;
CREATE TABLE groupmembers.aliases (
    id integer NOT NULL,
    objectid integer,
    alias text,
    isgroup integer,
    serverid bigint
);
ALTER TABLE groupmembers.aliases OWNER TO postgres;
CREATE SEQUENCE groupmembers.aliases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.aliases_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.aliases_id_seq OWNED BY groupmembers.aliases.id;
CREATE TABLE groupmembers.alreadyexists (
    link text NOT NULL
);
ALTER TABLE groupmembers.alreadyexists OWNER TO postgres;
CREATE TABLE groupmembers.apiurl (
    driveurl text,
    apiurl text NOT NULL
);
ALTER TABLE groupmembers.apiurl OWNER TO postgres;
COMMENT ON TABLE groupmembers.apiurl IS 'API Stored Image Link To Google Drive Link';
CREATE TABLE groupmembers.automatic (
    link text NOT NULL,
    fullname text,
    ingroup text,
    ingroup2 text,
    ingroup3 text,
    stagename text,
    aliases text
);
ALTER TABLE groupmembers.automatic OWNER TO postgres;
CREATE TABLE groupmembers.count (
    memberid integer NOT NULL,
    count integer
);
ALTER TABLE groupmembers.count OWNER TO postgres;
CREATE TABLE groupmembers.deadlinkfromuser (
    deadlink text,
    userid bigint,
    id integer NOT NULL,
    messageid bigint,
    idolid integer,
    guessinggame integer DEFAULT 0
);
ALTER TABLE groupmembers.deadlinkfromuser OWNER TO postgres;
CREATE SEQUENCE groupmembers.deadlinkfromuser_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.deadlinkfromuser_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.deadlinkfromuser_id_seq OWNED BY groupmembers.deadlinkfromuser.id;
CREATE TABLE groupmembers.deleted (
    link text,
    memberid integer,
    id integer NOT NULL
);
ALTER TABLE groupmembers.deleted OWNER TO postgres;
CREATE SEQUENCE groupmembers.deleted_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.deleted_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.deleted_id_seq OWNED BY groupmembers.deleted.id;
CREATE TABLE groupmembers.folders (
    id integer NOT NULL,
    folderid text,
    foldername text,
    memberid integer
);
ALTER TABLE groupmembers.folders OWNER TO postgres;
CREATE SEQUENCE groupmembers.folders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.folders_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.folders_id_seq OWNED BY groupmembers.folders.id;
CREATE TABLE groupmembers.forbiddenlinks (
    id integer NOT NULL,
    link text,
    idolid integer
);
ALTER TABLE groupmembers.forbiddenlinks OWNER TO postgres;
CREATE SEQUENCE groupmembers.forbiddenlinks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.forbiddenlinks_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.forbiddenlinks_id_seq OWNED BY groupmembers.forbiddenlinks.id;
CREATE TABLE groupmembers.groupfolders (
    id integer NOT NULL,
    folderid text,
    foldername text,
    groupid integer
);
ALTER TABLE groupmembers.groupfolders OWNER TO postgres;
CREATE SEQUENCE groupmembers.groupfolders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.groupfolders_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.groupfolders_id_seq OWNED BY groupmembers.groupfolders.id;
CREATE TABLE groupmembers.groups (
    groupid integer NOT NULL,
    groupname text,
    debutdate date,
    disbanddate date,
    description text,
    twitter text,
    youtube text,
    melon text,
    instagram text,
    vlive text,
    spotify text,
    fancafe text,
    facebook text,
    tiktok text,
    fandom text,
    company text,
    website text,
    thumbnail text,
    banner text,
    gender text,
    tags text
);
ALTER TABLE groupmembers.groups OWNER TO postgres;
CREATE SEQUENCE groupmembers.groups_groupid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.groups_groupid_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.groups_groupid_seq OWNED BY groupmembers.groups.groupid;
CREATE TABLE groupmembers.idoltogroup (
    id integer NOT NULL,
    idolid integer,
    groupid integer
);
ALTER TABLE groupmembers.idoltogroup OWNER TO postgres;
CREATE SEQUENCE groupmembers.idoltogroup_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.idoltogroup_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.idoltogroup_id_seq OWNED BY groupmembers.idoltogroup.id;
CREATE TABLE groupmembers.imagelinks (
    link text,
    memberid integer,
    id integer NOT NULL,
    groupphoto integer DEFAULT 0,
    facecount integer,
    filetype text
);
ALTER TABLE groupmembers.imagelinks OWNER TO postgres;
CREATE SEQUENCE groupmembers.images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.images_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.images_id_seq OWNED BY groupmembers.imagelinks.id;
CREATE TABLE groupmembers.member (
    fullname text,
    stagename text,
    id integer NOT NULL,
    formerfullname text,
    formerstagename text,
    birthdate date,
    birthcountry text,
    birthcity text,
    gender text,
    description text,
    height integer,
    twitter text,
    youtube text,
    melon text,
    instagram text,
    vlive text,
    spotify text,
    fancafe text,
    facebook text,
    tiktok text,
    zodiac text,
    thumbnail text,
    banner text,
    bloodtype text,
    tags text,
    difficulty text
);
ALTER TABLE groupmembers.member OWNER TO postgres;
CREATE SEQUENCE groupmembers.member_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.member_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.member_id_seq OWNED BY groupmembers.member.id;
CREATE TABLE groupmembers.restricted (
    channelid bigint NOT NULL,
    serverid bigint,
    sendhere integer
);
ALTER TABLE groupmembers.restricted OWNER TO postgres;
CREATE TABLE groupmembers.subfolders (
    id integer NOT NULL,
    folderid text,
    foldername text,
    memberid integer
);
ALTER TABLE groupmembers.subfolders OWNER TO postgres;
CREATE SEQUENCE groupmembers.subfolders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.subfolders_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.subfolders_id_seq OWNED BY groupmembers.subfolders.id;
CREATE TABLE groupmembers.unregisteredgroups (
    groupname text,
    debutdate date,
    disbanddate date,
    description text,
    twitter text,
    youtube text,
    melon text,
    instagram text,
    vlive text,
    spotify text,
    fancafe text,
    facebook text,
    tiktok text,
    fandom text,
    company text,
    website text,
    thumbnail text,
    banner text,
    gender text,
    tags text,
    id integer NOT NULL,
    notes text
);
ALTER TABLE groupmembers.unregisteredgroups OWNER TO postgres;
CREATE SEQUENCE groupmembers.unregisteredgroups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.unregisteredgroups_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.unregisteredgroups_id_seq OWNED BY groupmembers.unregisteredgroups.id;
CREATE TABLE groupmembers.unregisteredmembers (
    fullname text,
    stagename text,
    formerfullname text,
    formerstagename text,
    birthdate date,
    birthcountry text,
    birthcity text,
    gender text,
    description text,
    height integer,
    twitter text,
    youtube text,
    melon text,
    instagram text,
    vlive text,
    spotify text,
    fancafe text,
    facebook text,
    tiktok text,
    zodiac text,
    thumbnail text,
    banner text,
    bloodtype text,
    tags text,
    id integer NOT NULL,
    groupids text,
    notes text
);
ALTER TABLE groupmembers.unregisteredmembers OWNER TO postgres;
CREATE SEQUENCE groupmembers.unregisteredmembers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.unregisteredmembers_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.unregisteredmembers_id_seq OWNED BY groupmembers.unregisteredmembers.id;
CREATE TABLE groupmembers.uploadimagelinks (
    link text,
    memberid integer,
    id integer NOT NULL
);
ALTER TABLE groupmembers.uploadimagelinks OWNER TO postgres;
CREATE SEQUENCE groupmembers.uploadimagelinks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE groupmembers.uploadimagelinks_id_seq OWNER TO postgres;
ALTER SEQUENCE groupmembers.uploadimagelinks_id_seq OWNED BY groupmembers.uploadimagelinks.id;
CREATE TABLE kiyomi.idols (
    kiyomiid integer NOT NULL,
    fullname text,
    stagename text,
    ingroups text
);
ALTER TABLE kiyomi.idols OWNER TO postgres;
CREATE TABLE kiyomi.imagelink (
    link text NOT NULL,
    memberid integer
);
ALTER TABLE kiyomi.imagelink OWNER TO postgres;
CREATE TABLE kiyomi.imagelinks (
    link text NOT NULL,
    memberid integer
);
ALTER TABLE kiyomi.imagelinks OWNER TO postgres;
CREATE TABLE kiyomi.members (
    kiyomiid integer NOT NULL,
    fullname text,
    stagename text,
    ingroups text
);
ALTER TABLE kiyomi.members OWNER TO postgres;
CREATE TABLE lastfm.users (
    userid bigint NOT NULL,
    username text
);
ALTER TABLE lastfm.users OWNER TO postgres;
CREATE TABLE logging.channels (
    channelid bigint,
    server integer,
    id integer NOT NULL
);
ALTER TABLE logging.channels OWNER TO postgres;
CREATE SEQUENCE logging.channels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE logging.channels_id_seq OWNER TO postgres;
ALTER SEQUENCE logging.channels_id_seq OWNED BY logging.channels.id;
CREATE TABLE logging.servers (
    serverid bigint,
    channelid bigint,
    status integer,
    id integer NOT NULL,
    sendall integer
);
ALTER TABLE logging.servers OWNER TO postgres;
CREATE SEQUENCE logging.servers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE logging.servers_id_seq OWNER TO postgres;
ALTER SEQUENCE logging.servers_id_seq OWNED BY logging.servers.id;
CREATE TABLE patreon.cache (
    userid bigint NOT NULL,
    super integer
);
ALTER TABLE patreon.cache OWNER TO postgres;
CREATE TABLE patreon.users (
    userid bigint NOT NULL
);
ALTER TABLE patreon.users OWNER TO postgres;
COMMENT ON TABLE patreon.users IS 'Manually Add Super Patrons // Special Users';
CREATE TABLE reminders.reminders (
    id integer NOT NULL,
    userid bigint,
    reason text,
    "timestamp" timestamp with time zone
);
ALTER TABLE reminders.reminders OWNER TO postgres;
CREATE SEQUENCE reminders.reminders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE reminders.reminders_id_seq OWNER TO postgres;
ALTER SEQUENCE reminders.reminders_id_seq OWNED BY reminders.reminders.id;
CREATE TABLE reminders.timezones (
    userid bigint NOT NULL,
    timezone text
);
ALTER TABLE reminders.timezones OWNER TO postgres;
CREATE TABLE selfassignroles.channels (
    serverid bigint NOT NULL,
    channelid bigint
);
ALTER TABLE selfassignroles.channels OWNER TO postgres;
CREATE TABLE selfassignroles.roles (
    roleid bigint NOT NULL,
    rolename text,
    serverid bigint
);
ALTER TABLE selfassignroles.roles OWNER TO postgres;
CREATE TABLE stats.apiusage (
    id integer NOT NULL,
    endpoint text,
    keyused integer,
    called bigint
);
ALTER TABLE stats.apiusage OWNER TO postgres;
CREATE SEQUENCE stats.apiusage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE stats.apiusage_id_seq OWNER TO postgres;
ALTER SEQUENCE stats.apiusage_id_seq OWNED BY stats.apiusage.id;
CREATE TABLE stats.commands (
    sessionid integer,
    commandname text,
    count bigint,
    id bigint NOT NULL
);
ALTER TABLE stats.commands OWNER TO postgres;
CREATE SEQUENCE stats.commands1_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE stats.commands1_id_seq OWNER TO postgres;
ALTER SEQUENCE stats.commands1_id_seq OWNED BY stats.commands.id;
CREATE TABLE stats.guessinggame (
    userid bigint NOT NULL,
    easy integer,
    medium integer,
    hard integer
);
ALTER TABLE stats.guessinggame OWNER TO postgres;
CREATE TABLE stats.guilds (
    guildid bigint NOT NULL,
    name text,
    emojicount integer,
    region text,
    afktimeout integer,
    icon text,
    ownerid bigint,
    banner text,
    description text,
    mfalevel integer,
    splash text,
    nitrolevel integer,
    boosts integer,
    textchannelcount integer,
    voicechannelcount integer,
    categorycount integer,
    emojilimit integer,
    membercount integer,
    rolecount integer,
    shardid integer,
    createdate timestamp with time zone
);
ALTER TABLE stats.guilds OWNER TO postgres;
CREATE TABLE stats.leftguild (
    id bigint NOT NULL,
    name text,
    region text,
    ownerid bigint,
    membercount integer
);
ALTER TABLE stats.leftguild OWNER TO postgres;
CREATE TABLE stats.sessions (
    totalused bigint,
    session bigint,
    date date NOT NULL,
    sessionid integer NOT NULL
);
ALTER TABLE stats.sessions OWNER TO postgres;
COMMENT ON TABLE stats.sessions IS 'Contains Session Data';
CREATE SEQUENCE stats.sessions_sessionid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE stats.sessions_sessionid_seq OWNER TO postgres;
ALTER SEQUENCE stats.sessions_sessionid_seq OWNED BY stats.sessions.sessionid;
CREATE TABLE stats.unscramblegame (
    userid bigint NOT NULL,
    easy integer,
    medium integer,
    hard integer
);
ALTER TABLE stats.unscramblegame OWNER TO postgres;
CREATE TABLE twitch.alreadyposted (
    id integer NOT NULL,
    username text,
    channelid bigint
);
ALTER TABLE twitch.alreadyposted OWNER TO postgres;
CREATE SEQUENCE twitch.alreadyposted_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE twitch.alreadyposted_id_seq OWNER TO postgres;
ALTER SEQUENCE twitch.alreadyposted_id_seq OWNED BY twitch.alreadyposted.id;
CREATE TABLE twitch.channels (
    id integer NOT NULL,
    username text,
    guildid bigint
);
ALTER TABLE twitch.channels OWNER TO postgres;
CREATE SEQUENCE twitch.channels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE twitch.channels_id_seq OWNER TO postgres;
ALTER SEQUENCE twitch.channels_id_seq OWNED BY twitch.channels.id;
CREATE TABLE twitch.guilds (
    guildid bigint NOT NULL,
    channelid bigint,
    roleid bigint
);
ALTER TABLE twitch.guilds OWNER TO postgres;
CREATE TABLE weverse.channels (
    id integer NOT NULL,
    channelid bigint,
    communityname text,
    roleid bigint,
    commentsdisabled integer
);
ALTER TABLE weverse.channels OWNER TO postgres;
CREATE SEQUENCE weverse.channels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE weverse.channels_id_seq OWNER TO postgres;
ALTER SEQUENCE weverse.channels_id_seq OWNED BY weverse.channels.id;
CREATE TABLE youtube.links (
    id integer NOT NULL,
    link text,
    channelid bigint
);
ALTER TABLE youtube.links OWNER TO postgres;
CREATE SEQUENCE youtube.links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE youtube.links_id_seq OWNER TO postgres;
ALTER SEQUENCE youtube.links_id_seq OWNED BY youtube.links.id;
CREATE TABLE youtube.views (
    id integer NOT NULL,
    linkid integer,
    views text,
    date text
);
ALTER TABLE youtube.views OWNER TO postgres;
CREATE SEQUENCE youtube.views_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE youtube.views_id_seq OWNER TO postgres;
ALTER SEQUENCE youtube.views_id_seq OWNED BY youtube.views.id;
ALTER TABLE ONLY archive.archivedchannels ALTER COLUMN id SET DEFAULT nextval('archive.archivedchannels_id_seq'::regclass);
ALTER TABLE ONLY archive.channellist ALTER COLUMN id SET DEFAULT nextval('archive.channellist_id_seq'::regclass);
ALTER TABLE ONLY archive.driveids ALTER COLUMN id SET DEFAULT nextval('archive.driveids_id_seq'::regclass);
ALTER TABLE ONLY biasgame.winners ALTER COLUMN id SET DEFAULT nextval('biasgame.winners_id_seq'::regclass);
ALTER TABLE ONLY blackjack.cardvalues ALTER COLUMN id SET DEFAULT nextval('blackjack.cards_id_seq'::regclass);
ALTER TABLE ONLY blackjack.games ALTER COLUMN gameid SET DEFAULT nextval('blackjack.games_gameid_seq'::regclass);
ALTER TABLE ONLY blackjack.playingcards ALTER COLUMN id SET DEFAULT nextval('blackjack.playingcards_id_seq'::regclass);
ALTER TABLE ONLY currency.cardvalues ALTER COLUMN cardid SET DEFAULT nextval('currency.cardvalues_cardid_seq'::regclass);
ALTER TABLE ONLY currency.games ALTER COLUMN gameid SET DEFAULT nextval('currency.games_gameid_seq'::regclass);
ALTER TABLE ONLY dreamcatcher.dchdlinks ALTER COLUMN id SET DEFAULT nextval('dreamcatcher.dchdlinks_id_seq'::regclass);
ALTER TABLE ONLY general.botstatus ALTER COLUMN id SET DEFAULT nextval('general.botstatus_id_seq'::regclass);
ALTER TABLE ONLY general.customcommands ALTER COLUMN id SET DEFAULT nextval('general.customcommands_id_seq'::regclass);
ALTER TABLE ONLY general.notifications ALTER COLUMN id SET DEFAULT nextval('general.notifications_id_seq'::regclass);
ALTER TABLE ONLY gg.filteredgroups ALTER COLUMN id SET DEFAULT nextval('gg.filteredgroups_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.aliases ALTER COLUMN id SET DEFAULT nextval('groupmembers.aliases_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.deadlinkfromuser ALTER COLUMN id SET DEFAULT nextval('groupmembers.deadlinkfromuser_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.deleted ALTER COLUMN id SET DEFAULT nextval('groupmembers.deleted_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.folders ALTER COLUMN id SET DEFAULT nextval('groupmembers.folders_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.forbiddenlinks ALTER COLUMN id SET DEFAULT nextval('groupmembers.forbiddenlinks_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.groupfolders ALTER COLUMN id SET DEFAULT nextval('groupmembers.groupfolders_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.groups ALTER COLUMN groupid SET DEFAULT nextval('groupmembers.groups_groupid_seq'::regclass);
ALTER TABLE ONLY groupmembers.idoltogroup ALTER COLUMN id SET DEFAULT nextval('groupmembers.idoltogroup_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.imagelinks ALTER COLUMN id SET DEFAULT nextval('groupmembers.images_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.member ALTER COLUMN id SET DEFAULT nextval('groupmembers.member_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.subfolders ALTER COLUMN id SET DEFAULT nextval('groupmembers.subfolders_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.unregisteredgroups ALTER COLUMN id SET DEFAULT nextval('groupmembers.unregisteredgroups_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.unregisteredmembers ALTER COLUMN id SET DEFAULT nextval('groupmembers.unregisteredmembers_id_seq'::regclass);
ALTER TABLE ONLY groupmembers.uploadimagelinks ALTER COLUMN id SET DEFAULT nextval('groupmembers.uploadimagelinks_id_seq'::regclass);
ALTER TABLE ONLY logging.channels ALTER COLUMN id SET DEFAULT nextval('logging.channels_id_seq'::regclass);
ALTER TABLE ONLY logging.servers ALTER COLUMN id SET DEFAULT nextval('logging.servers_id_seq'::regclass);
ALTER TABLE ONLY reminders.reminders ALTER COLUMN id SET DEFAULT nextval('reminders.reminders_id_seq'::regclass);
ALTER TABLE ONLY stats.apiusage ALTER COLUMN id SET DEFAULT nextval('stats.apiusage_id_seq'::regclass);
ALTER TABLE ONLY stats.commands ALTER COLUMN id SET DEFAULT nextval('stats.commands1_id_seq'::regclass);
ALTER TABLE ONLY stats.sessions ALTER COLUMN sessionid SET DEFAULT nextval('stats.sessions_sessionid_seq'::regclass);
ALTER TABLE ONLY twitch.alreadyposted ALTER COLUMN id SET DEFAULT nextval('twitch.alreadyposted_id_seq'::regclass);
ALTER TABLE ONLY twitch.channels ALTER COLUMN id SET DEFAULT nextval('twitch.channels_id_seq'::regclass);
ALTER TABLE ONLY weverse.channels ALTER COLUMN id SET DEFAULT nextval('weverse.channels_id_seq'::regclass);
ALTER TABLE ONLY youtube.links ALTER COLUMN id SET DEFAULT nextval('youtube.links_id_seq'::regclass);
ALTER TABLE ONLY youtube.views ALTER COLUMN id SET DEFAULT nextval('youtube.views_id_seq'::regclass);
ALTER TABLE ONLY archive.channellist
    ADD CONSTRAINT "ChannelList_ChannelID_key" UNIQUE (channelid);
ALTER TABLE ONLY archive.driveids
    ADD CONSTRAINT "DriveIDs_LinkID_key" UNIQUE (linkid);
ALTER TABLE ONLY archive.archivedchannels
    ADD CONSTRAINT archivedchannels_pkey PRIMARY KEY (id);
ALTER TABLE ONLY archive.channellist
    ADD CONSTRAINT channellist_pkey PRIMARY KEY (id);
ALTER TABLE ONLY archive.driveids
    ADD CONSTRAINT driveids_pkey PRIMARY KEY (id);
ALTER TABLE ONLY biasgame.winners
    ADD CONSTRAINT winners_pkey PRIMARY KEY (id);
ALTER TABLE ONLY blackjack.cardvalues
    ADD CONSTRAINT cards_pkey PRIMARY KEY (name);
ALTER TABLE ONLY blackjack.currentstatus
    ADD CONSTRAINT currentstatus_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY blackjack.games
    ADD CONSTRAINT games_pkey PRIMARY KEY (gameid);
ALTER TABLE ONLY blackjack.playingcards
    ADD CONSTRAINT playingcards_pkey PRIMARY KEY (id);
ALTER TABLE ONLY currency.cardvalues
    ADD CONSTRAINT "CardValues_CardName_key" UNIQUE (cardname);
ALTER TABLE ONLY currency.currency
    ADD CONSTRAINT "Currency_UserID_key" UNIQUE (userid);
ALTER TABLE ONLY currency.games
    ADD CONSTRAINT "Games_Player1_key" UNIQUE (player1);
ALTER TABLE ONLY currency.games
    ADD CONSTRAINT "Games_Player2_key" UNIQUE (player2);
ALTER TABLE ONLY currency.levels
    ADD CONSTRAINT "Levels_pkey" PRIMARY KEY (userid);
ALTER TABLE ONLY currency.raffledata
    ADD CONSTRAINT "RaffleData_pkey" PRIMARY KEY (raffleid);
ALTER TABLE ONLY currency.raffle
    ADD CONSTRAINT "Raffle_pkey" PRIMARY KEY (raffleid);
ALTER TABLE ONLY currency.blackjack
    ADD CONSTRAINT blackjack_pkey PRIMARY KEY (gameid);
ALTER TABLE ONLY currency.cardvalues
    ADD CONSTRAINT cardvalues_pkey PRIMARY KEY (cardid);
ALTER TABLE ONLY currency.currency
    ADD CONSTRAINT currency_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY currency.games
    ADD CONSTRAINT games_pkey PRIMARY KEY (gameid);
ALTER TABLE ONLY currency.logging
    ADD CONSTRAINT logging_channelid_key UNIQUE (channelid);
ALTER TABLE ONLY currency.logging
    ADD CONSTRAINT logging_pkey PRIMARY KEY (channelid);
ALTER TABLE ONLY currency.loggingprivate
    ADD CONSTRAINT "loggingprivate_ChannelID_key" UNIQUE (channelid);
ALTER TABLE ONLY currency.loggingprivate
    ADD CONSTRAINT loggingprivate_pkey PRIMARY KEY (channelid);
ALTER TABLE ONLY dreamcatcher.dchdlinks
    ADD CONSTRAINT "DCHDLinks_Link_key" UNIQUE (link);
ALTER TABLE ONLY dreamcatcher.dchdlinks
    ADD CONSTRAINT dchdlinks_pkey PRIMARY KEY (id);
ALTER TABLE ONLY dreamcatcher.dcpost
    ADD CONSTRAINT dcpost_pkey PRIMARY KEY (postid);
ALTER TABLE ONLY dreamcatcher.dcurl
    ADD CONSTRAINT dcurl_pkey PRIMARY KEY (member);
ALTER TABLE ONLY dreamcatcher.dreamcatcher
    ADD CONSTRAINT dreamcatcher_pkey PRIMARY KEY (channelid);
ALTER TABLE ONLY general.tempchannels
    ADD CONSTRAINT "TempChannels_chanID_key" UNIQUE (chanid);
ALTER TABLE ONLY general.blacklisted
    ADD CONSTRAINT blacklisted_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY general.botstatus
    ADD CONSTRAINT botstatus_pkey PRIMARY KEY (id);
ALTER TABLE ONLY general.nword
    ADD CONSTRAINT counter_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY general.customcommands
    ADD CONSTRAINT customcommands_pkey PRIMARY KEY (id);
ALTER TABLE ONLY general.disabledinteractions
    ADD CONSTRAINT disabledinteractions_pkey PRIMARY KEY (serverid);
ALTER TABLE ONLY general.gamesdisabled
    ADD CONSTRAINT gamesdisabled_pkey PRIMARY KEY (channelid);
ALTER TABLE ONLY general.interactions
    ADD CONSTRAINT interactions_pkey PRIMARY KEY (url);
ALTER TABLE ONLY general.languages
    ADD CONSTRAINT languages_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY general.lastvoted
    ADD CONSTRAINT lastvoted_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY general.modmail
    ADD CONSTRAINT modmail2_pkey PRIMARY KEY (userid, channelid);
ALTER TABLE ONLY general.muteroles
    ADD CONSTRAINT muteroles_pkey PRIMARY KEY (roleid);
ALTER TABLE ONLY general.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);
ALTER TABLE ONLY general.serverprefix
    ADD CONSTRAINT serverprefix_pkey PRIMARY KEY (serverid);
ALTER TABLE ONLY general.tempchannels
    ADD CONSTRAINT tempchannels_pkey PRIMARY KEY (chanid);
ALTER TABLE ONLY general.welcome
    ADD CONSTRAINT welcome_pkey PRIMARY KEY (serverid);
ALTER TABLE ONLY general.welcomeroles
    ADD CONSTRAINT welcomeroles_pkey PRIMARY KEY (guildid);
ALTER TABLE ONLY gg.filteredgroups
    ADD CONSTRAINT filteredgroups_pkey PRIMARY KEY (id);
ALTER TABLE ONLY gg.filterenabled
    ADD CONSTRAINT filterenabled_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY groupmembers.count
    ADD CONSTRAINT "Count_MemberID_key" UNIQUE (memberid);
ALTER TABLE ONLY groupmembers.aliases
    ADD CONSTRAINT aliases_pkey PRIMARY KEY (id);
ALTER TABLE ONLY groupmembers.alreadyexists
    ADD CONSTRAINT alreadyexists_pkey PRIMARY KEY (link);
ALTER TABLE ONLY groupmembers.apiurl
    ADD CONSTRAINT apiurl_pkey PRIMARY KEY (apiurl);
ALTER TABLE ONLY groupmembers.automatic
    ADD CONSTRAINT "automatic_Link_key" UNIQUE (link);
ALTER TABLE ONLY groupmembers.automatic
    ADD CONSTRAINT automatic_pkey PRIMARY KEY (link);
ALTER TABLE ONLY groupmembers.count
    ADD CONSTRAINT count_pkey PRIMARY KEY (memberid);
ALTER TABLE ONLY groupmembers.deadlinkfromuser
    ADD CONSTRAINT "deadlinkfromuser_DeadLink_key" UNIQUE (deadlink);
ALTER TABLE ONLY groupmembers.deadlinkfromuser
    ADD CONSTRAINT deadlinkfromuser_pkey PRIMARY KEY (id);
ALTER TABLE ONLY groupmembers.deleted
    ADD CONSTRAINT "deleted_Link_key" UNIQUE (link);
ALTER TABLE ONLY groupmembers.deleted
    ADD CONSTRAINT deleted_pkey PRIMARY KEY (id);
ALTER TABLE ONLY groupmembers.folders
    ADD CONSTRAINT folders_pkey PRIMARY KEY (id);
ALTER TABLE ONLY groupmembers.forbiddenlinks
    ADD CONSTRAINT forbiddenlinks_pkey PRIMARY KEY (id);
ALTER TABLE ONLY groupmembers.groupfolders
    ADD CONSTRAINT groupfolders_pkey PRIMARY KEY (id);
ALTER TABLE ONLY groupmembers.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (groupid);
ALTER TABLE ONLY groupmembers.idoltogroup
    ADD CONSTRAINT idoltogroup_pkey PRIMARY KEY (id);
ALTER TABLE ONLY groupmembers.imagelinks
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);
ALTER TABLE ONLY groupmembers.imagelinks
    ADD CONSTRAINT links UNIQUE (link);
ALTER TABLE ONLY groupmembers.member
    ADD CONSTRAINT member_pkey PRIMARY KEY (id);
ALTER TABLE ONLY groupmembers.restricted
    ADD CONSTRAINT restricted_pkey PRIMARY KEY (channelid);
ALTER TABLE ONLY groupmembers.subfolders
    ADD CONSTRAINT subfolders_pkey PRIMARY KEY (id);
ALTER TABLE ONLY groupmembers.unregisteredgroups
    ADD CONSTRAINT unregisteredgroups_pkey PRIMARY KEY (id);
ALTER TABLE ONLY groupmembers.unregisteredmembers
    ADD CONSTRAINT unregisteredmembers_pkey PRIMARY KEY (id);
ALTER TABLE ONLY groupmembers.uploadimagelinks
    ADD CONSTRAINT uploadimagelinks_pkey PRIMARY KEY (id);
ALTER TABLE ONLY kiyomi.idols
    ADD CONSTRAINT idols_pkey PRIMARY KEY (kiyomiid);
ALTER TABLE ONLY kiyomi.imagelink
    ADD CONSTRAINT imagelink_pkey PRIMARY KEY (link);
ALTER TABLE ONLY kiyomi.imagelinks
    ADD CONSTRAINT imagelinks_pkey PRIMARY KEY (link);
ALTER TABLE ONLY kiyomi.members
    ADD CONSTRAINT members_pkey PRIMARY KEY (kiyomiid);
ALTER TABLE ONLY lastfm.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY logging.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (id);
ALTER TABLE ONLY logging.servers
    ADD CONSTRAINT servers_pkey PRIMARY KEY (id);
ALTER TABLE ONLY patreon.cache
    ADD CONSTRAINT cache_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY patreon.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY reminders.reminders
    ADD CONSTRAINT reminders_pkey PRIMARY KEY (id);
ALTER TABLE ONLY reminders.timezones
    ADD CONSTRAINT timezones_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY selfassignroles.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (serverid);
ALTER TABLE ONLY selfassignroles.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (roleid);
ALTER TABLE ONLY stats.apiusage
    ADD CONSTRAINT apiusage_pkey PRIMARY KEY (id);
ALTER TABLE ONLY stats.commands
    ADD CONSTRAINT commands1_pkey PRIMARY KEY (id);
ALTER TABLE ONLY stats.guessinggame
    ADD CONSTRAINT guessinggame_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY stats.guilds
    ADD CONSTRAINT guilds_pkey PRIMARY KEY (guildid);
ALTER TABLE ONLY stats.leftguild
    ADD CONSTRAINT leftguild_pkey PRIMARY KEY (id);
ALTER TABLE ONLY stats.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (date);
ALTER TABLE ONLY stats.unscramblegame
    ADD CONSTRAINT unscramblegame_pkey PRIMARY KEY (userid);
ALTER TABLE ONLY twitch.alreadyposted
    ADD CONSTRAINT alreadyposted_pkey PRIMARY KEY (id);
ALTER TABLE ONLY twitch.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (id);
ALTER TABLE ONLY twitch.guilds
    ADD CONSTRAINT guilds_pkey PRIMARY KEY (guildid);
ALTER TABLE ONLY weverse.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (id);
ALTER TABLE ONLY youtube.links
    ADD CONSTRAINT links_pkey PRIMARY KEY (id);
ALTER TABLE ONLY youtube.views
    ADD CONSTRAINT views_pkey PRIMARY KEY (id);
CREATE UNIQUE INDEX idol_group ON groupmembers.idoltogroup USING btree (idolid, groupid);
GRANT SELECT ON TABLE pg_catalog.pg_stat_database TO datadog;
