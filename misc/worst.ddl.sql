USE defaultdb;

DROP DATABASE IF EXISTS worst CASCADE;

CREATE DATABASE worst;

USE worst;

/*********************************/
/*            OBJECTS            */
/*********************************/
CREATE TABLE worst_models (
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

CREATE TABLE worst_reports (
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

CREATE TABLE worst_watch (
    -- pk
    id INT2 NOT NULL,
    -- fields
    ts TIMESTAMPTZ DEFAULT NOW() ON UPDATE NOW(),
    CONSTRAINT pk PRIMARY KEY (id)
);

INSERT INTO
    worst_watch (id)
VALUES
    (1);

CREATE TABLE worst_events (
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
