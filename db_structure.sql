--
-- PostgreSQL database dump
--

-- Dumped from database version 12.4 (Ubuntu 12.4-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.4 (Ubuntu 12.4-0ubuntu0.20.04.1)

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

--
-- Name: archive; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA archive;


ALTER SCHEMA archive OWNER TO postgres;

--
-- Name: biasgame; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA biasgame;


ALTER SCHEMA biasgame OWNER TO postgres;

--
-- Name: blackjack; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA blackjack;


ALTER SCHEMA blackjack OWNER TO postgres;

--
-- Name: currency; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA currency;


ALTER SCHEMA currency OWNER TO postgres;

--
-- Name: dreamcatcher; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA dreamcatcher;


ALTER SCHEMA dreamcatcher OWNER TO postgres;

--
-- Name: general; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA general;


ALTER SCHEMA general OWNER TO postgres;

--
-- Name: gg; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA gg;


ALTER SCHEMA gg OWNER TO postgres;

--
-- Name: groupmembers; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA groupmembers;


ALTER SCHEMA groupmembers OWNER TO postgres;

--
-- Name: kiyomi; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA kiyomi;


ALTER SCHEMA kiyomi OWNER TO postgres;

--
-- Name: lastfm; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA lastfm;


ALTER SCHEMA lastfm OWNER TO postgres;

--
-- Name: logging; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA logging;


ALTER SCHEMA logging OWNER TO postgres;

--
-- Name: patreon; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA patreon;


ALTER SCHEMA patreon OWNER TO postgres;

--
-- Name: pgagent; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA pgagent;


ALTER SCHEMA pgagent OWNER TO postgres;

--
-- Name: SCHEMA pgagent; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA pgagent IS 'pgAgent system tables';


--
-- Name: reminders; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA reminders;


ALTER SCHEMA reminders OWNER TO postgres;

--
-- Name: selfassignroles; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA selfassignroles;


ALTER SCHEMA selfassignroles OWNER TO postgres;

--
-- Name: stats; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA stats;


ALTER SCHEMA stats OWNER TO postgres;

--
-- Name: testdb; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA testdb;


ALTER SCHEMA testdb OWNER TO postgres;

--
-- Name: twitch; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA twitch;


ALTER SCHEMA twitch OWNER TO postgres;

--
-- Name: weverse; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA weverse;


ALTER SCHEMA weverse OWNER TO postgres;

--
-- Name: youtube; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA youtube;


ALTER SCHEMA youtube OWNER TO postgres;

--
-- Name: adminpack; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS adminpack WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION adminpack; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION adminpack IS 'administrative functions for PostgreSQL';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: archivedchannels; Type: TABLE; Schema: archive; Owner: postgres
--

CREATE TABLE archive.archivedchannels (
    filename text,
    filetype text,
    folderid text,
    channelid bigint,
    id integer NOT NULL
);


ALTER TABLE archive.archivedchannels OWNER TO postgres;

--
-- Name: archivedchannels_id_seq; Type: SEQUENCE; Schema: archive; Owner: postgres
--

CREATE SEQUENCE archive.archivedchannels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE archive.archivedchannels_id_seq OWNER TO postgres;

--
-- Name: archivedchannels_id_seq; Type: SEQUENCE OWNED BY; Schema: archive; Owner: postgres
--

ALTER SEQUENCE archive.archivedchannels_id_seq OWNED BY archive.archivedchannels.id;


--
-- Name: channellist; Type: TABLE; Schema: archive; Owner: postgres
--

CREATE TABLE archive.channellist (
    channelid bigint,
    guildid bigint,
    driveid text,
    name text,
    id integer NOT NULL
);


ALTER TABLE archive.channellist OWNER TO postgres;

--
-- Name: channellist_id_seq; Type: SEQUENCE; Schema: archive; Owner: postgres
--

CREATE SEQUENCE archive.channellist_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE archive.channellist_id_seq OWNER TO postgres;

--
-- Name: channellist_id_seq; Type: SEQUENCE OWNED BY; Schema: archive; Owner: postgres
--

ALTER SEQUENCE archive.channellist_id_seq OWNED BY archive.channellist.id;


--
-- Name: driveids; Type: TABLE; Schema: archive; Owner: postgres
--

CREATE TABLE archive.driveids (
    linkid text,
    name text,
    id integer NOT NULL
);


ALTER TABLE archive.driveids OWNER TO postgres;

--
-- Name: driveids_id_seq; Type: SEQUENCE; Schema: archive; Owner: postgres
--

CREATE SEQUENCE archive.driveids_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE archive.driveids_id_seq OWNER TO postgres;

--
-- Name: driveids_id_seq; Type: SEQUENCE OWNED BY; Schema: archive; Owner: postgres
--

ALTER SEQUENCE archive.driveids_id_seq OWNED BY archive.driveids.id;


--
-- Name: winners; Type: TABLE; Schema: biasgame; Owner: postgres
--

CREATE TABLE biasgame.winners (
    id integer NOT NULL,
    idolid integer,
    userid bigint,
    wins integer
);


ALTER TABLE biasgame.winners OWNER TO postgres;

--
-- Name: winners_id_seq; Type: SEQUENCE; Schema: biasgame; Owner: postgres
--

CREATE SEQUENCE biasgame.winners_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE biasgame.winners_id_seq OWNER TO postgres;

--
-- Name: winners_id_seq; Type: SEQUENCE OWNED BY; Schema: biasgame; Owner: postgres
--

ALTER SEQUENCE biasgame.winners_id_seq OWNED BY biasgame.winners.id;


--
-- Name: cardvalues; Type: TABLE; Schema: blackjack; Owner: postgres
--

CREATE TABLE blackjack.cardvalues (
    id integer NOT NULL,
    name text NOT NULL,
    value integer
);


ALTER TABLE blackjack.cardvalues OWNER TO postgres;

--
-- Name: cards_id_seq; Type: SEQUENCE; Schema: blackjack; Owner: postgres
--

CREATE SEQUENCE blackjack.cards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE blackjack.cards_id_seq OWNER TO postgres;

--
-- Name: cards_id_seq; Type: SEQUENCE OWNED BY; Schema: blackjack; Owner: postgres
--

ALTER SEQUENCE blackjack.cards_id_seq OWNED BY blackjack.cardvalues.id;


--
-- Name: currentstatus; Type: TABLE; Schema: blackjack; Owner: postgres
--

CREATE TABLE blackjack.currentstatus (
    userid bigint NOT NULL,
    stand integer,
    inhand text,
    total integer,
    acesused text
);


ALTER TABLE blackjack.currentstatus OWNER TO postgres;

--
-- Name: games; Type: TABLE; Schema: blackjack; Owner: postgres
--

CREATE TABLE blackjack.games (
    gameid integer NOT NULL,
    player1 bigint,
    player2 bigint,
    bid1 text,
    bid2 text,
    channelid bigint
);


ALTER TABLE blackjack.games OWNER TO postgres;

--
-- Name: games_gameid_seq; Type: SEQUENCE; Schema: blackjack; Owner: postgres
--

CREATE SEQUENCE blackjack.games_gameid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE blackjack.games_gameid_seq OWNER TO postgres;

--
-- Name: games_gameid_seq; Type: SEQUENCE OWNED BY; Schema: blackjack; Owner: postgres
--

ALTER SEQUENCE blackjack.games_gameid_seq OWNED BY blackjack.games.gameid;


--
-- Name: playingcards; Type: TABLE; Schema: blackjack; Owner: postgres
--

CREATE TABLE blackjack.playingcards (
    id integer NOT NULL,
    cardvalueid integer,
    bgidolid integer,
    filename text
);


ALTER TABLE blackjack.playingcards OWNER TO postgres;

--
-- Name: playingcards_id_seq; Type: SEQUENCE; Schema: blackjack; Owner: postgres
--

CREATE SEQUENCE blackjack.playingcards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE blackjack.playingcards_id_seq OWNER TO postgres;

--
-- Name: playingcards_id_seq; Type: SEQUENCE OWNED BY; Schema: blackjack; Owner: postgres
--

ALTER SEQUENCE blackjack.playingcards_id_seq OWNED BY blackjack.playingcards.id;


--
-- Name: blackjack; Type: TABLE; Schema: currency; Owner: postgres
--

CREATE TABLE currency.blackjack (
    gameid integer NOT NULL,
    cardid integer,
    "position" integer
);


ALTER TABLE currency.blackjack OWNER TO postgres;

--
-- Name: cardvalues; Type: TABLE; Schema: currency; Owner: postgres
--

CREATE TABLE currency.cardvalues (
    cardname text,
    value integer,
    cardid integer NOT NULL
);


ALTER TABLE currency.cardvalues OWNER TO postgres;

--
-- Name: cardvalues_cardid_seq; Type: SEQUENCE; Schema: currency; Owner: postgres
--

CREATE SEQUENCE currency.cardvalues_cardid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE currency.cardvalues_cardid_seq OWNER TO postgres;

--
-- Name: cardvalues_cardid_seq; Type: SEQUENCE OWNED BY; Schema: currency; Owner: postgres
--

ALTER SEQUENCE currency.cardvalues_cardid_seq OWNED BY currency.cardvalues.cardid;


--
-- Name: currency; Type: TABLE; Schema: currency; Owner: postgres
--

CREATE TABLE currency.currency (
    userid bigint NOT NULL,
    money text
);


ALTER TABLE currency.currency OWNER TO postgres;

--
-- Name: games; Type: TABLE; Schema: currency; Owner: postgres
--

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

--
-- Name: games_gameid_seq; Type: SEQUENCE; Schema: currency; Owner: postgres
--

CREATE SEQUENCE currency.games_gameid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE currency.games_gameid_seq OWNER TO postgres;

--
-- Name: games_gameid_seq; Type: SEQUENCE OWNED BY; Schema: currency; Owner: postgres
--

ALTER SEQUENCE currency.games_gameid_seq OWNED BY currency.games.gameid;


--
-- Name: levels; Type: TABLE; Schema: currency; Owner: postgres
--

CREATE TABLE currency.levels (
    userid bigint NOT NULL,
    rob integer,
    daily integer,
    beg integer,
    profile integer,
    profilexp integer
);


ALTER TABLE currency.levels OWNER TO postgres;

--
-- Name: logging; Type: TABLE; Schema: currency; Owner: postgres
--

CREATE TABLE currency.logging (
    channelid text NOT NULL
);


ALTER TABLE currency.logging OWNER TO postgres;

--
-- Name: loggingprivate; Type: TABLE; Schema: currency; Owner: postgres
--

CREATE TABLE currency.loggingprivate (
    channelid text NOT NULL
);


ALTER TABLE currency.loggingprivate OWNER TO postgres;

--
-- Name: raffle; Type: TABLE; Schema: currency; Owner: postgres
--

CREATE TABLE currency.raffle (
    raffleid integer NOT NULL,
    winner integer,
    amount integer,
    finished integer
);


ALTER TABLE currency.raffle OWNER TO postgres;

--
-- Name: raffledata; Type: TABLE; Schema: currency; Owner: postgres
--

CREATE TABLE currency.raffledata (
    raffleid integer NOT NULL,
    userid text,
    amount integer
);


ALTER TABLE currency.raffledata OWNER TO postgres;

--
-- Name: valueplaces; Type: TABLE; Schema: currency; Owner: postgres
--

CREATE TABLE currency.valueplaces (
    name text,
    length integer,
    length2 integer,
    length3 integer
);


ALTER TABLE currency.valueplaces OWNER TO postgres;

--
-- Name: dchdlinks; Type: TABLE; Schema: dreamcatcher; Owner: postgres
--

CREATE TABLE dreamcatcher.dchdlinks (
    link text,
    member text,
    postnumber integer,
    id integer NOT NULL
);


ALTER TABLE dreamcatcher.dchdlinks OWNER TO postgres;

--
-- Name: dchdlinks_id_seq; Type: SEQUENCE; Schema: dreamcatcher; Owner: postgres
--

CREATE SEQUENCE dreamcatcher.dchdlinks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dreamcatcher.dchdlinks_id_seq OWNER TO postgres;

--
-- Name: dchdlinks_id_seq; Type: SEQUENCE OWNED BY; Schema: dreamcatcher; Owner: postgres
--

ALTER SEQUENCE dreamcatcher.dchdlinks_id_seq OWNED BY dreamcatcher.dchdlinks.id;


--
-- Name: dcpost; Type: TABLE; Schema: dreamcatcher; Owner: postgres
--

CREATE TABLE dreamcatcher.dcpost (
    postid integer NOT NULL
);


ALTER TABLE dreamcatcher.dcpost OWNER TO postgres;

--
-- Name: dcurl; Type: TABLE; Schema: dreamcatcher; Owner: postgres
--

CREATE TABLE dreamcatcher.dcurl (
    url text NOT NULL,
    member text NOT NULL
);


ALTER TABLE dreamcatcher.dcurl OWNER TO postgres;

--
-- Name: dreamcatcher; Type: TABLE; Schema: dreamcatcher; Owner: postgres
--

CREATE TABLE dreamcatcher.dreamcatcher (
    channelid bigint NOT NULL,
    roleid bigint
);


ALTER TABLE dreamcatcher.dreamcatcher OWNER TO postgres;

--
-- Name: blacklisted; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.blacklisted (
    userid bigint NOT NULL
);


ALTER TABLE general.blacklisted OWNER TO postgres;

--
-- Name: botstatus; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.botstatus (
    id integer NOT NULL,
    status text
);


ALTER TABLE general.botstatus OWNER TO postgres;

--
-- Name: botstatus_id_seq; Type: SEQUENCE; Schema: general; Owner: postgres
--

CREATE SEQUENCE general.botstatus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE general.botstatus_id_seq OWNER TO postgres;

--
-- Name: botstatus_id_seq; Type: SEQUENCE OWNED BY; Schema: general; Owner: postgres
--

ALTER SEQUENCE general.botstatus_id_seq OWNED BY general.botstatus.id;


--
-- Name: customcommands; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.customcommands (
    id integer NOT NULL,
    serverid bigint,
    commandname text,
    message text
);


ALTER TABLE general.customcommands OWNER TO postgres;

--
-- Name: customcommands_id_seq; Type: SEQUENCE; Schema: general; Owner: postgres
--

CREATE SEQUENCE general.customcommands_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE general.customcommands_id_seq OWNER TO postgres;

--
-- Name: customcommands_id_seq; Type: SEQUENCE OWNED BY; Schema: general; Owner: postgres
--

ALTER SEQUENCE general.customcommands_id_seq OWNED BY general.customcommands.id;


--
-- Name: disabledinteractions; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.disabledinteractions (
    serverid bigint NOT NULL,
    interactions text
);


ALTER TABLE general.disabledinteractions OWNER TO postgres;

--
-- Name: interactions; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.interactions (
    url text NOT NULL,
    interaction text
);


ALTER TABLE general.interactions OWNER TO postgres;

--
-- Name: languages; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.languages (
    userid bigint NOT NULL,
    language text
);


ALTER TABLE general.languages OWNER TO postgres;

--
-- Name: lastvoted; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.lastvoted (
    userid bigint NOT NULL,
    votetimestamp timestamp with time zone DEFAULT now()
);


ALTER TABLE general.lastvoted OWNER TO postgres;

--
-- Name: modmail; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.modmail (
    userid bigint NOT NULL,
    channelid bigint NOT NULL
);


ALTER TABLE general.modmail OWNER TO postgres;

--
-- Name: muteroles; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.muteroles (
    roleid bigint NOT NULL
);


ALTER TABLE general.muteroles OWNER TO postgres;

--
-- Name: notifications; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.notifications (
    id integer NOT NULL,
    guildid bigint,
    userid bigint,
    phrase text
);


ALTER TABLE general.notifications OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: general; Owner: postgres
--

CREATE SEQUENCE general.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE general.notifications_id_seq OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: general; Owner: postgres
--

ALTER SEQUENCE general.notifications_id_seq OWNED BY general.notifications.id;


--
-- Name: nword; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.nword (
    userid bigint NOT NULL,
    nword integer
);


ALTER TABLE general.nword OWNER TO postgres;

--
-- Name: serverprefix; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.serverprefix (
    serverid bigint NOT NULL,
    prefix text
);


ALTER TABLE general.serverprefix OWNER TO postgres;

--
-- Name: tempchannels; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.tempchannels (
    chanid bigint NOT NULL,
    delay bigint
);


ALTER TABLE general.tempchannels OWNER TO postgres;

--
-- Name: welcome; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.welcome (
    channelid bigint,
    serverid bigint NOT NULL,
    message text,
    enabled integer
);


ALTER TABLE general.welcome OWNER TO postgres;

--
-- Name: TABLE welcome; Type: COMMENT; Schema: general; Owner: postgres
--

COMMENT ON TABLE general.welcome IS 'Welcome Messages ';


--
-- Name: welcomeroles; Type: TABLE; Schema: general; Owner: postgres
--

CREATE TABLE general.welcomeroles (
    guildid bigint NOT NULL,
    roleid bigint
);


ALTER TABLE general.welcomeroles OWNER TO postgres;

--
-- Name: filteredgroups; Type: TABLE; Schema: gg; Owner: postgres
--

CREATE TABLE gg.filteredgroups (
    id integer NOT NULL,
    userid bigint,
    groupid integer
);


ALTER TABLE gg.filteredgroups OWNER TO postgres;

--
-- Name: filteredgroups_id_seq; Type: SEQUENCE; Schema: gg; Owner: postgres
--

CREATE SEQUENCE gg.filteredgroups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE gg.filteredgroups_id_seq OWNER TO postgres;

--
-- Name: filteredgroups_id_seq; Type: SEQUENCE OWNED BY; Schema: gg; Owner: postgres
--

ALTER SEQUENCE gg.filteredgroups_id_seq OWNED BY gg.filteredgroups.id;


--
-- Name: filterenabled; Type: TABLE; Schema: gg; Owner: postgres
--

CREATE TABLE gg.filterenabled (
    userid bigint NOT NULL
);


ALTER TABLE gg.filterenabled OWNER TO postgres;

--
-- Name: aliases; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.aliases (
    id integer NOT NULL,
    objectid integer,
    alias text,
    isgroup integer,
    serverid bigint
);


ALTER TABLE groupmembers.aliases OWNER TO postgres;

--
-- Name: aliases_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.aliases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.aliases_id_seq OWNER TO postgres;

--
-- Name: aliases_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.aliases_id_seq OWNED BY groupmembers.aliases.id;


--
-- Name: alreadyexists; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.alreadyexists (
    link text NOT NULL
);


ALTER TABLE groupmembers.alreadyexists OWNER TO postgres;

--
-- Name: apiurl; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.apiurl (
    driveurl text,
    apiurl text NOT NULL
);


ALTER TABLE groupmembers.apiurl OWNER TO postgres;

--
-- Name: TABLE apiurl; Type: COMMENT; Schema: groupmembers; Owner: postgres
--

COMMENT ON TABLE groupmembers.apiurl IS 'API Stored Image Link To Google Drive Link';


--
-- Name: automatic; Type: TABLE; Schema: groupmembers; Owner: postgres
--

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

--
-- Name: count; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.count (
    memberid integer NOT NULL,
    count integer
);


ALTER TABLE groupmembers.count OWNER TO postgres;

--
-- Name: deadlinkfromuser; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.deadlinkfromuser (
    deadlink text,
    userid bigint,
    id integer NOT NULL,
    messageid bigint,
    idolid integer,
    guessinggame integer DEFAULT 0
);


ALTER TABLE groupmembers.deadlinkfromuser OWNER TO postgres;

--
-- Name: deadlinkfromuser_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.deadlinkfromuser_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.deadlinkfromuser_id_seq OWNER TO postgres;

--
-- Name: deadlinkfromuser_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.deadlinkfromuser_id_seq OWNED BY groupmembers.deadlinkfromuser.id;


--
-- Name: deleted; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.deleted (
    link text,
    memberid integer,
    id integer NOT NULL
);


ALTER TABLE groupmembers.deleted OWNER TO postgres;

--
-- Name: deleted_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.deleted_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.deleted_id_seq OWNER TO postgres;

--
-- Name: deleted_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.deleted_id_seq OWNED BY groupmembers.deleted.id;


--
-- Name: folders; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.folders (
    id integer NOT NULL,
    folderid text,
    foldername text,
    memberid integer
);


ALTER TABLE groupmembers.folders OWNER TO postgres;

--
-- Name: folders_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.folders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.folders_id_seq OWNER TO postgres;

--
-- Name: folders_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.folders_id_seq OWNED BY groupmembers.folders.id;


--
-- Name: forbiddenlinks; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.forbiddenlinks (
    id integer NOT NULL,
    link text,
    idolid integer
);


ALTER TABLE groupmembers.forbiddenlinks OWNER TO postgres;

--
-- Name: forbiddenlinks_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.forbiddenlinks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.forbiddenlinks_id_seq OWNER TO postgres;

--
-- Name: forbiddenlinks_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.forbiddenlinks_id_seq OWNED BY groupmembers.forbiddenlinks.id;


--
-- Name: groupfolders; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.groupfolders (
    id integer NOT NULL,
    folderid text,
    foldername text,
    groupid integer
);


ALTER TABLE groupmembers.groupfolders OWNER TO postgres;

--
-- Name: groupfolders_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.groupfolders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.groupfolders_id_seq OWNER TO postgres;

--
-- Name: groupfolders_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.groupfolders_id_seq OWNED BY groupmembers.groupfolders.id;


--
-- Name: groups; Type: TABLE; Schema: groupmembers; Owner: postgres
--

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

--
-- Name: groups_groupid_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.groups_groupid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.groups_groupid_seq OWNER TO postgres;

--
-- Name: groups_groupid_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.groups_groupid_seq OWNED BY groupmembers.groups.groupid;


--
-- Name: idoltogroup; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.idoltogroup (
    id integer NOT NULL,
    idolid integer,
    groupid integer
);


ALTER TABLE groupmembers.idoltogroup OWNER TO postgres;

--
-- Name: idoltogroup_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.idoltogroup_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.idoltogroup_id_seq OWNER TO postgres;

--
-- Name: idoltogroup_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.idoltogroup_id_seq OWNED BY groupmembers.idoltogroup.id;


--
-- Name: imagelinks; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.imagelinks (
    link text,
    memberid integer,
    id integer NOT NULL,
    groupphoto integer DEFAULT 0,
    facecount integer,
    filetype text
);


ALTER TABLE groupmembers.imagelinks OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.images_id_seq OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.images_id_seq OWNED BY groupmembers.imagelinks.id;


--
-- Name: member; Type: TABLE; Schema: groupmembers; Owner: postgres
--

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

--
-- Name: member_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.member_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.member_id_seq OWNER TO postgres;

--
-- Name: member_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.member_id_seq OWNED BY groupmembers.member.id;


--
-- Name: restricted; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.restricted (
    channelid bigint NOT NULL,
    serverid bigint,
    sendhere integer
);


ALTER TABLE groupmembers.restricted OWNER TO postgres;

--
-- Name: subfolders; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.subfolders (
    id integer NOT NULL,
    folderid text,
    foldername text,
    memberid integer
);


ALTER TABLE groupmembers.subfolders OWNER TO postgres;

--
-- Name: subfolders_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.subfolders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.subfolders_id_seq OWNER TO postgres;

--
-- Name: subfolders_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.subfolders_id_seq OWNED BY groupmembers.subfolders.id;


--
-- Name: unregisteredgroups; Type: TABLE; Schema: groupmembers; Owner: postgres
--

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

--
-- Name: unregisteredgroups_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.unregisteredgroups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.unregisteredgroups_id_seq OWNER TO postgres;

--
-- Name: unregisteredgroups_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.unregisteredgroups_id_seq OWNED BY groupmembers.unregisteredgroups.id;


--
-- Name: unregisteredmembers; Type: TABLE; Schema: groupmembers; Owner: postgres
--

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

--
-- Name: unregisteredmembers_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.unregisteredmembers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.unregisteredmembers_id_seq OWNER TO postgres;

--
-- Name: unregisteredmembers_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.unregisteredmembers_id_seq OWNED BY groupmembers.unregisteredmembers.id;


--
-- Name: uploadimagelinks; Type: TABLE; Schema: groupmembers; Owner: postgres
--

CREATE TABLE groupmembers.uploadimagelinks (
    link text,
    memberid integer,
    id integer NOT NULL
);


ALTER TABLE groupmembers.uploadimagelinks OWNER TO postgres;

--
-- Name: uploadimagelinks_id_seq; Type: SEQUENCE; Schema: groupmembers; Owner: postgres
--

CREATE SEQUENCE groupmembers.uploadimagelinks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE groupmembers.uploadimagelinks_id_seq OWNER TO postgres;

--
-- Name: uploadimagelinks_id_seq; Type: SEQUENCE OWNED BY; Schema: groupmembers; Owner: postgres
--

ALTER SEQUENCE groupmembers.uploadimagelinks_id_seq OWNED BY groupmembers.uploadimagelinks.id;


--
-- Name: idols; Type: TABLE; Schema: kiyomi; Owner: postgres
--

CREATE TABLE kiyomi.idols (
    kiyomiid integer NOT NULL,
    fullname text,
    stagename text,
    ingroups text
);


ALTER TABLE kiyomi.idols OWNER TO postgres;

--
-- Name: imagelink; Type: TABLE; Schema: kiyomi; Owner: postgres
--

CREATE TABLE kiyomi.imagelink (
    link text NOT NULL,
    memberid integer
);


ALTER TABLE kiyomi.imagelink OWNER TO postgres;

--
-- Name: imagelinks; Type: TABLE; Schema: kiyomi; Owner: postgres
--

CREATE TABLE kiyomi.imagelinks (
    link text NOT NULL,
    memberid integer
);


ALTER TABLE kiyomi.imagelinks OWNER TO postgres;

--
-- Name: members; Type: TABLE; Schema: kiyomi; Owner: postgres
--

CREATE TABLE kiyomi.members (
    kiyomiid integer NOT NULL,
    fullname text,
    stagename text,
    ingroups text
);


ALTER TABLE kiyomi.members OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: lastfm; Owner: postgres
--

CREATE TABLE lastfm.users (
    userid bigint NOT NULL,
    username text
);


ALTER TABLE lastfm.users OWNER TO postgres;

--
-- Name: channels; Type: TABLE; Schema: logging; Owner: postgres
--

CREATE TABLE logging.channels (
    channelid bigint,
    server integer,
    id integer NOT NULL
);


ALTER TABLE logging.channels OWNER TO postgres;

--
-- Name: channels_id_seq; Type: SEQUENCE; Schema: logging; Owner: postgres
--

CREATE SEQUENCE logging.channels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE logging.channels_id_seq OWNER TO postgres;

--
-- Name: channels_id_seq; Type: SEQUENCE OWNED BY; Schema: logging; Owner: postgres
--

ALTER SEQUENCE logging.channels_id_seq OWNED BY logging.channels.id;


--
-- Name: servers; Type: TABLE; Schema: logging; Owner: postgres
--

CREATE TABLE logging.servers (
    serverid bigint,
    channelid bigint,
    status integer,
    id integer NOT NULL,
    sendall integer
);


ALTER TABLE logging.servers OWNER TO postgres;

--
-- Name: servers_id_seq; Type: SEQUENCE; Schema: logging; Owner: postgres
--

CREATE SEQUENCE logging.servers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE logging.servers_id_seq OWNER TO postgres;

--
-- Name: servers_id_seq; Type: SEQUENCE OWNED BY; Schema: logging; Owner: postgres
--

ALTER SEQUENCE logging.servers_id_seq OWNED BY logging.servers.id;


--
-- Name: cache; Type: TABLE; Schema: patreon; Owner: postgres
--

CREATE TABLE patreon.cache (
    userid bigint NOT NULL,
    super integer
);


ALTER TABLE patreon.cache OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: patreon; Owner: postgres
--

CREATE TABLE patreon.users (
    userid bigint NOT NULL
);


ALTER TABLE patreon.users OWNER TO postgres;

--
-- Name: TABLE users; Type: COMMENT; Schema: patreon; Owner: postgres
--

COMMENT ON TABLE patreon.users IS 'Manually Add Super Patrons // Special Users';


--
-- Name: reminders; Type: TABLE; Schema: reminders; Owner: postgres
--

CREATE TABLE reminders.reminders (
    id integer NOT NULL,
    userid bigint,
    reason text,
    "timestamp" timestamp with time zone
);


ALTER TABLE reminders.reminders OWNER TO postgres;

--
-- Name: reminders_id_seq; Type: SEQUENCE; Schema: reminders; Owner: postgres
--

CREATE SEQUENCE reminders.reminders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE reminders.reminders_id_seq OWNER TO postgres;

--
-- Name: reminders_id_seq; Type: SEQUENCE OWNED BY; Schema: reminders; Owner: postgres
--

ALTER SEQUENCE reminders.reminders_id_seq OWNED BY reminders.reminders.id;


--
-- Name: timezones; Type: TABLE; Schema: reminders; Owner: postgres
--

CREATE TABLE reminders.timezones (
    userid bigint NOT NULL,
    timezone text
);


ALTER TABLE reminders.timezones OWNER TO postgres;

--
-- Name: channels; Type: TABLE; Schema: selfassignroles; Owner: postgres
--

CREATE TABLE selfassignroles.channels (
    serverid bigint NOT NULL,
    channelid bigint
);


ALTER TABLE selfassignroles.channels OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: selfassignroles; Owner: postgres
--

CREATE TABLE selfassignroles.roles (
    roleid bigint NOT NULL,
    rolename text,
    serverid bigint
);


ALTER TABLE selfassignroles.roles OWNER TO postgres;

--
-- Name: apiusage; Type: TABLE; Schema: stats; Owner: postgres
--

CREATE TABLE stats.apiusage (
    id integer NOT NULL,
    endpoint text,
    keyused integer,
    called bigint
);


ALTER TABLE stats.apiusage OWNER TO postgres;

--
-- Name: apiusage_id_seq; Type: SEQUENCE; Schema: stats; Owner: postgres
--

CREATE SEQUENCE stats.apiusage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE stats.apiusage_id_seq OWNER TO postgres;

--
-- Name: apiusage_id_seq; Type: SEQUENCE OWNED BY; Schema: stats; Owner: postgres
--

ALTER SEQUENCE stats.apiusage_id_seq OWNED BY stats.apiusage.id;


--
-- Name: commands; Type: TABLE; Schema: stats; Owner: postgres
--

CREATE TABLE stats.commands (
    sessionid integer,
    commandname text,
    count bigint,
    id bigint NOT NULL
);


ALTER TABLE stats.commands OWNER TO postgres;

--
-- Name: commands1_id_seq; Type: SEQUENCE; Schema: stats; Owner: postgres
--

CREATE SEQUENCE stats.commands1_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE stats.commands1_id_seq OWNER TO postgres;

--
-- Name: commands1_id_seq; Type: SEQUENCE OWNED BY; Schema: stats; Owner: postgres
--

ALTER SEQUENCE stats.commands1_id_seq OWNED BY stats.commands.id;


--
-- Name: guessinggame; Type: TABLE; Schema: stats; Owner: postgres
--

CREATE TABLE stats.guessinggame (
    userid bigint NOT NULL,
    easy integer,
    medium integer,
    hard integer
);


ALTER TABLE stats.guessinggame OWNER TO postgres;

--
-- Name: guilds; Type: TABLE; Schema: stats; Owner: postgres
--

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

--
-- Name: leftguild; Type: TABLE; Schema: stats; Owner: postgres
--

CREATE TABLE stats.leftguild (
    id bigint NOT NULL,
    name text,
    region text,
    ownerid bigint,
    membercount integer
);


ALTER TABLE stats.leftguild OWNER TO postgres;

--
-- Name: sessions; Type: TABLE; Schema: stats; Owner: postgres
--

CREATE TABLE stats.sessions (
    totalused bigint,
    session bigint,
    date date NOT NULL,
    sessionid integer NOT NULL
);


ALTER TABLE stats.sessions OWNER TO postgres;

--
-- Name: TABLE sessions; Type: COMMENT; Schema: stats; Owner: postgres
--

COMMENT ON TABLE stats.sessions IS 'Contains Session Data';


--
-- Name: sessions_sessionid_seq; Type: SEQUENCE; Schema: stats; Owner: postgres
--

CREATE SEQUENCE stats.sessions_sessionid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE stats.sessions_sessionid_seq OWNER TO postgres;

--
-- Name: sessions_sessionid_seq; Type: SEQUENCE OWNED BY; Schema: stats; Owner: postgres
--

ALTER SEQUENCE stats.sessions_sessionid_seq OWNED BY stats.sessions.sessionid;


--
-- Name: alreadyposted; Type: TABLE; Schema: twitch; Owner: postgres
--

CREATE TABLE twitch.alreadyposted (
    id integer NOT NULL,
    username text,
    channelid bigint
);


ALTER TABLE twitch.alreadyposted OWNER TO postgres;

--
-- Name: alreadyposted_id_seq; Type: SEQUENCE; Schema: twitch; Owner: postgres
--

CREATE SEQUENCE twitch.alreadyposted_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE twitch.alreadyposted_id_seq OWNER TO postgres;

--
-- Name: alreadyposted_id_seq; Type: SEQUENCE OWNED BY; Schema: twitch; Owner: postgres
--

ALTER SEQUENCE twitch.alreadyposted_id_seq OWNED BY twitch.alreadyposted.id;


--
-- Name: channels; Type: TABLE; Schema: twitch; Owner: postgres
--

CREATE TABLE twitch.channels (
    id integer NOT NULL,
    username text,
    guildid bigint
);


ALTER TABLE twitch.channels OWNER TO postgres;

--
-- Name: channels_id_seq; Type: SEQUENCE; Schema: twitch; Owner: postgres
--

CREATE SEQUENCE twitch.channels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE twitch.channels_id_seq OWNER TO postgres;

--
-- Name: channels_id_seq; Type: SEQUENCE OWNED BY; Schema: twitch; Owner: postgres
--

ALTER SEQUENCE twitch.channels_id_seq OWNED BY twitch.channels.id;


--
-- Name: guilds; Type: TABLE; Schema: twitch; Owner: postgres
--

CREATE TABLE twitch.guilds (
    guildid bigint NOT NULL,
    channelid bigint,
    roleid bigint
);


ALTER TABLE twitch.guilds OWNER TO postgres;

--
-- Name: channels; Type: TABLE; Schema: weverse; Owner: postgres
--

CREATE TABLE weverse.channels (
    id integer NOT NULL,
    channelid bigint,
    communityname text,
    roleid bigint,
    commentsdisabled integer
);


ALTER TABLE weverse.channels OWNER TO postgres;

--
-- Name: channels_id_seq; Type: SEQUENCE; Schema: weverse; Owner: postgres
--

CREATE SEQUENCE weverse.channels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE weverse.channels_id_seq OWNER TO postgres;

--
-- Name: channels_id_seq; Type: SEQUENCE OWNED BY; Schema: weverse; Owner: postgres
--

ALTER SEQUENCE weverse.channels_id_seq OWNED BY weverse.channels.id;


--
-- Name: links; Type: TABLE; Schema: youtube; Owner: postgres
--

CREATE TABLE youtube.links (
    id integer NOT NULL,
    link text,
    channelid bigint
);


ALTER TABLE youtube.links OWNER TO postgres;

--
-- Name: links_id_seq; Type: SEQUENCE; Schema: youtube; Owner: postgres
--

CREATE SEQUENCE youtube.links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE youtube.links_id_seq OWNER TO postgres;

--
-- Name: links_id_seq; Type: SEQUENCE OWNED BY; Schema: youtube; Owner: postgres
--

ALTER SEQUENCE youtube.links_id_seq OWNED BY youtube.links.id;


--
-- Name: views; Type: TABLE; Schema: youtube; Owner: postgres
--

CREATE TABLE youtube.views (
    id integer NOT NULL,
    linkid integer,
    views text,
    date text
);


ALTER TABLE youtube.views OWNER TO postgres;

--
-- Name: views_id_seq; Type: SEQUENCE; Schema: youtube; Owner: postgres
--

CREATE SEQUENCE youtube.views_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE youtube.views_id_seq OWNER TO postgres;

--
-- Name: views_id_seq; Type: SEQUENCE OWNED BY; Schema: youtube; Owner: postgres
--

ALTER SEQUENCE youtube.views_id_seq OWNED BY youtube.views.id;


--
-- Name: archivedchannels id; Type: DEFAULT; Schema: archive; Owner: postgres
--

ALTER TABLE ONLY archive.archivedchannels ALTER COLUMN id SET DEFAULT nextval('archive.archivedchannels_id_seq'::regclass);


--
-- Name: channellist id; Type: DEFAULT; Schema: archive; Owner: postgres
--

ALTER TABLE ONLY archive.channellist ALTER COLUMN id SET DEFAULT nextval('archive.channellist_id_seq'::regclass);


--
-- Name: driveids id; Type: DEFAULT; Schema: archive; Owner: postgres
--

ALTER TABLE ONLY archive.driveids ALTER COLUMN id SET DEFAULT nextval('archive.driveids_id_seq'::regclass);


--
-- Name: winners id; Type: DEFAULT; Schema: biasgame; Owner: postgres
--

ALTER TABLE ONLY biasgame.winners ALTER COLUMN id SET DEFAULT nextval('biasgame.winners_id_seq'::regclass);


--
-- Name: cardvalues id; Type: DEFAULT; Schema: blackjack; Owner: postgres
--

ALTER TABLE ONLY blackjack.cardvalues ALTER COLUMN id SET DEFAULT nextval('blackjack.cards_id_seq'::regclass);


--
-- Name: games gameid; Type: DEFAULT; Schema: blackjack; Owner: postgres
--

ALTER TABLE ONLY blackjack.games ALTER COLUMN gameid SET DEFAULT nextval('blackjack.games_gameid_seq'::regclass);


--
-- Name: playingcards id; Type: DEFAULT; Schema: blackjack; Owner: postgres
--

ALTER TABLE ONLY blackjack.playingcards ALTER COLUMN id SET DEFAULT nextval('blackjack.playingcards_id_seq'::regclass);


--
-- Name: cardvalues cardid; Type: DEFAULT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.cardvalues ALTER COLUMN cardid SET DEFAULT nextval('currency.cardvalues_cardid_seq'::regclass);


--
-- Name: games gameid; Type: DEFAULT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.games ALTER COLUMN gameid SET DEFAULT nextval('currency.games_gameid_seq'::regclass);


--
-- Name: dchdlinks id; Type: DEFAULT; Schema: dreamcatcher; Owner: postgres
--

ALTER TABLE ONLY dreamcatcher.dchdlinks ALTER COLUMN id SET DEFAULT nextval('dreamcatcher.dchdlinks_id_seq'::regclass);


--
-- Name: botstatus id; Type: DEFAULT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.botstatus ALTER COLUMN id SET DEFAULT nextval('general.botstatus_id_seq'::regclass);


--
-- Name: customcommands id; Type: DEFAULT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.customcommands ALTER COLUMN id SET DEFAULT nextval('general.customcommands_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.notifications ALTER COLUMN id SET DEFAULT nextval('general.notifications_id_seq'::regclass);


--
-- Name: filteredgroups id; Type: DEFAULT; Schema: gg; Owner: postgres
--

ALTER TABLE ONLY gg.filteredgroups ALTER COLUMN id SET DEFAULT nextval('gg.filteredgroups_id_seq'::regclass);


--
-- Name: aliases id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.aliases ALTER COLUMN id SET DEFAULT nextval('groupmembers.aliases_id_seq'::regclass);


--
-- Name: deadlinkfromuser id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.deadlinkfromuser ALTER COLUMN id SET DEFAULT nextval('groupmembers.deadlinkfromuser_id_seq'::regclass);


--
-- Name: deleted id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.deleted ALTER COLUMN id SET DEFAULT nextval('groupmembers.deleted_id_seq'::regclass);


--
-- Name: folders id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.folders ALTER COLUMN id SET DEFAULT nextval('groupmembers.folders_id_seq'::regclass);


--
-- Name: forbiddenlinks id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.forbiddenlinks ALTER COLUMN id SET DEFAULT nextval('groupmembers.forbiddenlinks_id_seq'::regclass);


--
-- Name: groupfolders id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.groupfolders ALTER COLUMN id SET DEFAULT nextval('groupmembers.groupfolders_id_seq'::regclass);


--
-- Name: groups groupid; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.groups ALTER COLUMN groupid SET DEFAULT nextval('groupmembers.groups_groupid_seq'::regclass);


--
-- Name: idoltogroup id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.idoltogroup ALTER COLUMN id SET DEFAULT nextval('groupmembers.idoltogroup_id_seq'::regclass);


--
-- Name: imagelinks id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.imagelinks ALTER COLUMN id SET DEFAULT nextval('groupmembers.images_id_seq'::regclass);


--
-- Name: member id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.member ALTER COLUMN id SET DEFAULT nextval('groupmembers.member_id_seq'::regclass);


--
-- Name: subfolders id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.subfolders ALTER COLUMN id SET DEFAULT nextval('groupmembers.subfolders_id_seq'::regclass);


--
-- Name: unregisteredgroups id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.unregisteredgroups ALTER COLUMN id SET DEFAULT nextval('groupmembers.unregisteredgroups_id_seq'::regclass);


--
-- Name: unregisteredmembers id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.unregisteredmembers ALTER COLUMN id SET DEFAULT nextval('groupmembers.unregisteredmembers_id_seq'::regclass);


--
-- Name: uploadimagelinks id; Type: DEFAULT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.uploadimagelinks ALTER COLUMN id SET DEFAULT nextval('groupmembers.uploadimagelinks_id_seq'::regclass);


--
-- Name: channels id; Type: DEFAULT; Schema: logging; Owner: postgres
--

ALTER TABLE ONLY logging.channels ALTER COLUMN id SET DEFAULT nextval('logging.channels_id_seq'::regclass);


--
-- Name: servers id; Type: DEFAULT; Schema: logging; Owner: postgres
--

ALTER TABLE ONLY logging.servers ALTER COLUMN id SET DEFAULT nextval('logging.servers_id_seq'::regclass);


--
-- Name: reminders id; Type: DEFAULT; Schema: reminders; Owner: postgres
--

ALTER TABLE ONLY reminders.reminders ALTER COLUMN id SET DEFAULT nextval('reminders.reminders_id_seq'::regclass);


--
-- Name: apiusage id; Type: DEFAULT; Schema: stats; Owner: postgres
--

ALTER TABLE ONLY stats.apiusage ALTER COLUMN id SET DEFAULT nextval('stats.apiusage_id_seq'::regclass);


--
-- Name: commands id; Type: DEFAULT; Schema: stats; Owner: postgres
--

ALTER TABLE ONLY stats.commands ALTER COLUMN id SET DEFAULT nextval('stats.commands1_id_seq'::regclass);


--
-- Name: sessions sessionid; Type: DEFAULT; Schema: stats; Owner: postgres
--

ALTER TABLE ONLY stats.sessions ALTER COLUMN sessionid SET DEFAULT nextval('stats.sessions_sessionid_seq'::regclass);


--
-- Name: alreadyposted id; Type: DEFAULT; Schema: twitch; Owner: postgres
--

ALTER TABLE ONLY twitch.alreadyposted ALTER COLUMN id SET DEFAULT nextval('twitch.alreadyposted_id_seq'::regclass);


--
-- Name: channels id; Type: DEFAULT; Schema: twitch; Owner: postgres
--

ALTER TABLE ONLY twitch.channels ALTER COLUMN id SET DEFAULT nextval('twitch.channels_id_seq'::regclass);


--
-- Name: channels id; Type: DEFAULT; Schema: weverse; Owner: postgres
--

ALTER TABLE ONLY weverse.channels ALTER COLUMN id SET DEFAULT nextval('weverse.channels_id_seq'::regclass);


--
-- Name: links id; Type: DEFAULT; Schema: youtube; Owner: postgres
--

ALTER TABLE ONLY youtube.links ALTER COLUMN id SET DEFAULT nextval('youtube.links_id_seq'::regclass);


--
-- Name: views id; Type: DEFAULT; Schema: youtube; Owner: postgres
--

ALTER TABLE ONLY youtube.views ALTER COLUMN id SET DEFAULT nextval('youtube.views_id_seq'::regclass);


--
-- Name: channellist ChannelList_ChannelID_key; Type: CONSTRAINT; Schema: archive; Owner: postgres
--

ALTER TABLE ONLY archive.channellist
    ADD CONSTRAINT "ChannelList_ChannelID_key" UNIQUE (channelid);


--
-- Name: driveids DriveIDs_LinkID_key; Type: CONSTRAINT; Schema: archive; Owner: postgres
--

ALTER TABLE ONLY archive.driveids
    ADD CONSTRAINT "DriveIDs_LinkID_key" UNIQUE (linkid);


--
-- Name: archivedchannels archivedchannels_pkey; Type: CONSTRAINT; Schema: archive; Owner: postgres
--

ALTER TABLE ONLY archive.archivedchannels
    ADD CONSTRAINT archivedchannels_pkey PRIMARY KEY (id);


--
-- Name: channellist channellist_pkey; Type: CONSTRAINT; Schema: archive; Owner: postgres
--

ALTER TABLE ONLY archive.channellist
    ADD CONSTRAINT channellist_pkey PRIMARY KEY (id);


--
-- Name: driveids driveids_pkey; Type: CONSTRAINT; Schema: archive; Owner: postgres
--

ALTER TABLE ONLY archive.driveids
    ADD CONSTRAINT driveids_pkey PRIMARY KEY (id);


--
-- Name: winners winners_pkey; Type: CONSTRAINT; Schema: biasgame; Owner: postgres
--

ALTER TABLE ONLY biasgame.winners
    ADD CONSTRAINT winners_pkey PRIMARY KEY (id);


--
-- Name: cardvalues cards_pkey; Type: CONSTRAINT; Schema: blackjack; Owner: postgres
--

ALTER TABLE ONLY blackjack.cardvalues
    ADD CONSTRAINT cards_pkey PRIMARY KEY (name);


--
-- Name: currentstatus currentstatus_pkey; Type: CONSTRAINT; Schema: blackjack; Owner: postgres
--

ALTER TABLE ONLY blackjack.currentstatus
    ADD CONSTRAINT currentstatus_pkey PRIMARY KEY (userid);


--
-- Name: games games_pkey; Type: CONSTRAINT; Schema: blackjack; Owner: postgres
--

ALTER TABLE ONLY blackjack.games
    ADD CONSTRAINT games_pkey PRIMARY KEY (gameid);


--
-- Name: playingcards playingcards_pkey; Type: CONSTRAINT; Schema: blackjack; Owner: postgres
--

ALTER TABLE ONLY blackjack.playingcards
    ADD CONSTRAINT playingcards_pkey PRIMARY KEY (id);


--
-- Name: cardvalues CardValues_CardName_key; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.cardvalues
    ADD CONSTRAINT "CardValues_CardName_key" UNIQUE (cardname);


--
-- Name: currency Currency_UserID_key; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.currency
    ADD CONSTRAINT "Currency_UserID_key" UNIQUE (userid);


--
-- Name: games Games_Player1_key; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.games
    ADD CONSTRAINT "Games_Player1_key" UNIQUE (player1);


--
-- Name: games Games_Player2_key; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.games
    ADD CONSTRAINT "Games_Player2_key" UNIQUE (player2);


--
-- Name: levels Levels_pkey; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.levels
    ADD CONSTRAINT "Levels_pkey" PRIMARY KEY (userid);


--
-- Name: raffledata RaffleData_pkey; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.raffledata
    ADD CONSTRAINT "RaffleData_pkey" PRIMARY KEY (raffleid);


--
-- Name: raffle Raffle_pkey; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.raffle
    ADD CONSTRAINT "Raffle_pkey" PRIMARY KEY (raffleid);


--
-- Name: blackjack blackjack_pkey; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.blackjack
    ADD CONSTRAINT blackjack_pkey PRIMARY KEY (gameid);


--
-- Name: cardvalues cardvalues_pkey; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.cardvalues
    ADD CONSTRAINT cardvalues_pkey PRIMARY KEY (cardid);


--
-- Name: currency currency_pkey; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.currency
    ADD CONSTRAINT currency_pkey PRIMARY KEY (userid);


--
-- Name: games games_pkey; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.games
    ADD CONSTRAINT games_pkey PRIMARY KEY (gameid);


--
-- Name: logging logging_channelid_key; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.logging
    ADD CONSTRAINT logging_channelid_key UNIQUE (channelid);


--
-- Name: logging logging_pkey; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.logging
    ADD CONSTRAINT logging_pkey PRIMARY KEY (channelid);


--
-- Name: loggingprivate loggingprivate_ChannelID_key; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.loggingprivate
    ADD CONSTRAINT "loggingprivate_ChannelID_key" UNIQUE (channelid);


--
-- Name: loggingprivate loggingprivate_pkey; Type: CONSTRAINT; Schema: currency; Owner: postgres
--

ALTER TABLE ONLY currency.loggingprivate
    ADD CONSTRAINT loggingprivate_pkey PRIMARY KEY (channelid);


--
-- Name: dchdlinks DCHDLinks_Link_key; Type: CONSTRAINT; Schema: dreamcatcher; Owner: postgres
--

ALTER TABLE ONLY dreamcatcher.dchdlinks
    ADD CONSTRAINT "DCHDLinks_Link_key" UNIQUE (link);


--
-- Name: dchdlinks dchdlinks_pkey; Type: CONSTRAINT; Schema: dreamcatcher; Owner: postgres
--

ALTER TABLE ONLY dreamcatcher.dchdlinks
    ADD CONSTRAINT dchdlinks_pkey PRIMARY KEY (id);


--
-- Name: dcpost dcpost_pkey; Type: CONSTRAINT; Schema: dreamcatcher; Owner: postgres
--

ALTER TABLE ONLY dreamcatcher.dcpost
    ADD CONSTRAINT dcpost_pkey PRIMARY KEY (postid);


--
-- Name: dcurl dcurl_pkey; Type: CONSTRAINT; Schema: dreamcatcher; Owner: postgres
--

ALTER TABLE ONLY dreamcatcher.dcurl
    ADD CONSTRAINT dcurl_pkey PRIMARY KEY (member);


--
-- Name: dreamcatcher dreamcatcher_pkey; Type: CONSTRAINT; Schema: dreamcatcher; Owner: postgres
--

ALTER TABLE ONLY dreamcatcher.dreamcatcher
    ADD CONSTRAINT dreamcatcher_pkey PRIMARY KEY (channelid);


--
-- Name: tempchannels TempChannels_chanID_key; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.tempchannels
    ADD CONSTRAINT "TempChannels_chanID_key" UNIQUE (chanid);


--
-- Name: blacklisted blacklisted_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.blacklisted
    ADD CONSTRAINT blacklisted_pkey PRIMARY KEY (userid);


--
-- Name: botstatus botstatus_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.botstatus
    ADD CONSTRAINT botstatus_pkey PRIMARY KEY (id);


--
-- Name: nword counter_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.nword
    ADD CONSTRAINT counter_pkey PRIMARY KEY (userid);


--
-- Name: customcommands customcommands_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.customcommands
    ADD CONSTRAINT customcommands_pkey PRIMARY KEY (id);


--
-- Name: disabledinteractions disabledinteractions_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.disabledinteractions
    ADD CONSTRAINT disabledinteractions_pkey PRIMARY KEY (serverid);


--
-- Name: interactions interactions_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.interactions
    ADD CONSTRAINT interactions_pkey PRIMARY KEY (url);


--
-- Name: languages languages_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.languages
    ADD CONSTRAINT languages_pkey PRIMARY KEY (userid);


--
-- Name: lastvoted lastvoted_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.lastvoted
    ADD CONSTRAINT lastvoted_pkey PRIMARY KEY (userid);


--
-- Name: modmail modmail2_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.modmail
    ADD CONSTRAINT modmail2_pkey PRIMARY KEY (userid, channelid);


--
-- Name: muteroles muteroles_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.muteroles
    ADD CONSTRAINT muteroles_pkey PRIMARY KEY (roleid);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: serverprefix serverprefix_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.serverprefix
    ADD CONSTRAINT serverprefix_pkey PRIMARY KEY (serverid);


--
-- Name: tempchannels tempchannels_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.tempchannels
    ADD CONSTRAINT tempchannels_pkey PRIMARY KEY (chanid);


--
-- Name: welcome welcome_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.welcome
    ADD CONSTRAINT welcome_pkey PRIMARY KEY (serverid);


--
-- Name: welcomeroles welcomeroles_pkey; Type: CONSTRAINT; Schema: general; Owner: postgres
--

ALTER TABLE ONLY general.welcomeroles
    ADD CONSTRAINT welcomeroles_pkey PRIMARY KEY (guildid);


--
-- Name: filteredgroups filteredgroups_pkey; Type: CONSTRAINT; Schema: gg; Owner: postgres
--

ALTER TABLE ONLY gg.filteredgroups
    ADD CONSTRAINT filteredgroups_pkey PRIMARY KEY (id);


--
-- Name: filterenabled filterenabled_pkey; Type: CONSTRAINT; Schema: gg; Owner: postgres
--

ALTER TABLE ONLY gg.filterenabled
    ADD CONSTRAINT filterenabled_pkey PRIMARY KEY (userid);


--
-- Name: count Count_MemberID_key; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.count
    ADD CONSTRAINT "Count_MemberID_key" UNIQUE (memberid);


--
-- Name: aliases aliases_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.aliases
    ADD CONSTRAINT aliases_pkey PRIMARY KEY (id);


--
-- Name: alreadyexists alreadyexists_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.alreadyexists
    ADD CONSTRAINT alreadyexists_pkey PRIMARY KEY (link);


--
-- Name: apiurl apiurl_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.apiurl
    ADD CONSTRAINT apiurl_pkey PRIMARY KEY (apiurl);


--
-- Name: automatic automatic_Link_key; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.automatic
    ADD CONSTRAINT "automatic_Link_key" UNIQUE (link);


--
-- Name: automatic automatic_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.automatic
    ADD CONSTRAINT automatic_pkey PRIMARY KEY (link);


--
-- Name: count count_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.count
    ADD CONSTRAINT count_pkey PRIMARY KEY (memberid);


--
-- Name: deadlinkfromuser deadlinkfromuser_DeadLink_key; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.deadlinkfromuser
    ADD CONSTRAINT "deadlinkfromuser_DeadLink_key" UNIQUE (deadlink);


--
-- Name: deadlinkfromuser deadlinkfromuser_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.deadlinkfromuser
    ADD CONSTRAINT deadlinkfromuser_pkey PRIMARY KEY (id);


--
-- Name: deleted deleted_Link_key; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.deleted
    ADD CONSTRAINT "deleted_Link_key" UNIQUE (link);


--
-- Name: deleted deleted_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.deleted
    ADD CONSTRAINT deleted_pkey PRIMARY KEY (id);


--
-- Name: folders folders_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.folders
    ADD CONSTRAINT folders_pkey PRIMARY KEY (id);


--
-- Name: forbiddenlinks forbiddenlinks_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.forbiddenlinks
    ADD CONSTRAINT forbiddenlinks_pkey PRIMARY KEY (id);


--
-- Name: groupfolders groupfolders_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.groupfolders
    ADD CONSTRAINT groupfolders_pkey PRIMARY KEY (id);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (groupid);


--
-- Name: idoltogroup idoltogroup_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.idoltogroup
    ADD CONSTRAINT idoltogroup_pkey PRIMARY KEY (id);


--
-- Name: imagelinks images_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.imagelinks
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- Name: imagelinks links; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.imagelinks
    ADD CONSTRAINT links UNIQUE (link);


--
-- Name: member member_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.member
    ADD CONSTRAINT member_pkey PRIMARY KEY (id);


--
-- Name: restricted restricted_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.restricted
    ADD CONSTRAINT restricted_pkey PRIMARY KEY (channelid);


--
-- Name: subfolders subfolders_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.subfolders
    ADD CONSTRAINT subfolders_pkey PRIMARY KEY (id);


--
-- Name: unregisteredgroups unregisteredgroups_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.unregisteredgroups
    ADD CONSTRAINT unregisteredgroups_pkey PRIMARY KEY (id);


--
-- Name: unregisteredmembers unregisteredmembers_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.unregisteredmembers
    ADD CONSTRAINT unregisteredmembers_pkey PRIMARY KEY (id);


--
-- Name: uploadimagelinks uploadimagelinks_pkey; Type: CONSTRAINT; Schema: groupmembers; Owner: postgres
--

ALTER TABLE ONLY groupmembers.uploadimagelinks
    ADD CONSTRAINT uploadimagelinks_pkey PRIMARY KEY (id);


--
-- Name: idols idols_pkey; Type: CONSTRAINT; Schema: kiyomi; Owner: postgres
--

ALTER TABLE ONLY kiyomi.idols
    ADD CONSTRAINT idols_pkey PRIMARY KEY (kiyomiid);


--
-- Name: imagelink imagelink_pkey; Type: CONSTRAINT; Schema: kiyomi; Owner: postgres
--

ALTER TABLE ONLY kiyomi.imagelink
    ADD CONSTRAINT imagelink_pkey PRIMARY KEY (link);


--
-- Name: imagelinks imagelinks_pkey; Type: CONSTRAINT; Schema: kiyomi; Owner: postgres
--

ALTER TABLE ONLY kiyomi.imagelinks
    ADD CONSTRAINT imagelinks_pkey PRIMARY KEY (link);


--
-- Name: members members_pkey; Type: CONSTRAINT; Schema: kiyomi; Owner: postgres
--

ALTER TABLE ONLY kiyomi.members
    ADD CONSTRAINT members_pkey PRIMARY KEY (kiyomiid);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: lastfm; Owner: postgres
--

ALTER TABLE ONLY lastfm.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (userid);


--
-- Name: channels channels_pkey; Type: CONSTRAINT; Schema: logging; Owner: postgres
--

ALTER TABLE ONLY logging.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (id);


--
-- Name: servers servers_pkey; Type: CONSTRAINT; Schema: logging; Owner: postgres
--

ALTER TABLE ONLY logging.servers
    ADD CONSTRAINT servers_pkey PRIMARY KEY (id);


--
-- Name: cache cache_pkey; Type: CONSTRAINT; Schema: patreon; Owner: postgres
--

ALTER TABLE ONLY patreon.cache
    ADD CONSTRAINT cache_pkey PRIMARY KEY (userid);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: patreon; Owner: postgres
--

ALTER TABLE ONLY patreon.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (userid);


--
-- Name: reminders reminders_pkey; Type: CONSTRAINT; Schema: reminders; Owner: postgres
--

ALTER TABLE ONLY reminders.reminders
    ADD CONSTRAINT reminders_pkey PRIMARY KEY (id);


--
-- Name: timezones timezones_pkey; Type: CONSTRAINT; Schema: reminders; Owner: postgres
--

ALTER TABLE ONLY reminders.timezones
    ADD CONSTRAINT timezones_pkey PRIMARY KEY (userid);


--
-- Name: channels channels_pkey; Type: CONSTRAINT; Schema: selfassignroles; Owner: postgres
--

ALTER TABLE ONLY selfassignroles.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (serverid);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: selfassignroles; Owner: postgres
--

ALTER TABLE ONLY selfassignroles.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (roleid);


--
-- Name: apiusage apiusage_pkey; Type: CONSTRAINT; Schema: stats; Owner: postgres
--

ALTER TABLE ONLY stats.apiusage
    ADD CONSTRAINT apiusage_pkey PRIMARY KEY (id);


--
-- Name: commands commands1_pkey; Type: CONSTRAINT; Schema: stats; Owner: postgres
--

ALTER TABLE ONLY stats.commands
    ADD CONSTRAINT commands1_pkey PRIMARY KEY (id);


--
-- Name: guessinggame guessinggame_pkey; Type: CONSTRAINT; Schema: stats; Owner: postgres
--

ALTER TABLE ONLY stats.guessinggame
    ADD CONSTRAINT guessinggame_pkey PRIMARY KEY (userid);


--
-- Name: guilds guilds_pkey; Type: CONSTRAINT; Schema: stats; Owner: postgres
--

ALTER TABLE ONLY stats.guilds
    ADD CONSTRAINT guilds_pkey PRIMARY KEY (guildid);


--
-- Name: leftguild leftguild_pkey; Type: CONSTRAINT; Schema: stats; Owner: postgres
--

ALTER TABLE ONLY stats.leftguild
    ADD CONSTRAINT leftguild_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: stats; Owner: postgres
--

ALTER TABLE ONLY stats.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (date);


--
-- Name: alreadyposted alreadyposted_pkey; Type: CONSTRAINT; Schema: twitch; Owner: postgres
--

ALTER TABLE ONLY twitch.alreadyposted
    ADD CONSTRAINT alreadyposted_pkey PRIMARY KEY (id);


--
-- Name: channels channels_pkey; Type: CONSTRAINT; Schema: twitch; Owner: postgres
--

ALTER TABLE ONLY twitch.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (id);


--
-- Name: guilds guilds_pkey; Type: CONSTRAINT; Schema: twitch; Owner: postgres
--

ALTER TABLE ONLY twitch.guilds
    ADD CONSTRAINT guilds_pkey PRIMARY KEY (guildid);


--
-- Name: channels channels_pkey; Type: CONSTRAINT; Schema: weverse; Owner: postgres
--

ALTER TABLE ONLY weverse.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (id);


--
-- Name: links links_pkey; Type: CONSTRAINT; Schema: youtube; Owner: postgres
--

ALTER TABLE ONLY youtube.links
    ADD CONSTRAINT links_pkey PRIMARY KEY (id);


--
-- Name: views views_pkey; Type: CONSTRAINT; Schema: youtube; Owner: postgres
--

ALTER TABLE ONLY youtube.views
    ADD CONSTRAINT views_pkey PRIMARY KEY (id);


--
-- Name: TABLE pg_stat_database; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_database TO datadog;


--
-- PostgreSQL database dump complete
--

