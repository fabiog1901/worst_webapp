-- as user root
USE defaultdb;

DROP DATABASE IF EXISTS worst CASCADE;

CREATE DATABASE worst;
create schema worst.internal;

create user worst with password 'worst';
create user worst_dml with password 'worst_dml';
create user worst_select with password 'worst_select';

revoke connect on database worst from public;
revoke usage, create on schema worst.public from public;

grant connect on database worst to worst;
grant connect on database worst to worst_dml;
grant connect on database worst to worst_select;

grant usage, create on schema worst.public to worst;
grant usage, create on schema worst.internal to worst;

grant usage on schema worst.public to worst_dml;
grant usage on schema worst.public to worst_select;

USE worst;
ALTER DEFAULT PRIVILEGES FOR ALL ROLES GRANT ALL ON TABLES TO worst WITH GRANT OPTION;
ALTER DEFAULT PRIVILEGES FOR ALL ROLES GRANT SELECT,INSERT,UPDATE,DELETE ON TABLES TO worst_dml WITH GRANT OPTION;
ALTER DEFAULT PRIVILEGES FOR ALL ROLES GRANT SELECT ON TABLES TO worst_select WITH GRANT OPTION;


USE worst;

CREATE TABLE internal.models (
    -- pk
    name STRING NOT NULL,
    -- fields
    skema JSONB,
    -- audit info
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by STRING NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW() ON UPDATE NOW(),
    updated_by STRING NULL,
    CONSTRAINT pk PRIMARY KEY (name)
);

CREATE TABLE internal.reports (
    -- pk
    name STRING NOT NULL,
    -- fields
    sql_stmt STRING,
    -- audit info
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by STRING NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW() ON UPDATE NOW(),
    updated_by STRING NULL,
    CONSTRAINT pk PRIMARY KEY (name)
);

CREATE TABLE internal.watch (
    -- pk
    id INT2 NOT NULL,
    -- fields
    ts TIMESTAMPTZ DEFAULT NOW() ON UPDATE NOW(),
    CONSTRAINT pk PRIMARY KEY (id)
);

INSERT INTO
    internal.watch (id)
VALUES
    (1);

CREATE TABLE internal.events (
    object STRING,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    username STRING,
    ACTION STRING,
    details STRING,
    CONSTRAINT pk PRIMARY KEY (object, ts, username)
) WITH (
    ttl = 'on',
    ttl_expiration_expression = '(ts::INT8 + 86400 * 30)::TIMESTAMPTZ',
    ttl_job_cron = '15 5 * * *'
);
