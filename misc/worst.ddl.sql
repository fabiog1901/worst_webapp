USE defaultdb;

DROP DATABASE IF EXISTS worst CASCADE;

CREATE DATABASE worst;

USE worst;

ALTER DATABASE worst CONFIGURE ZONE USING 
    range_min_bytes = 134217728,
    range_max_bytes = 536870912,
    gc.ttlseconds = 3600,
    num_replicas = 1,
    constraints = '[]',
    lease_preferences = '[]';


CREATE TABLE worst_users (
    user_id STRING NOT NULL,
    full_name STRING,
    email STRING,
    hashed_password STRING,
    is_disabled STRING,
    scopes STRING[],
    failed_attempts INT2 NULL,
    CONSTRAINT pk PRIMARY KEY (user_id),
    CONSTRAINT failed_attempts_max_3 CHECK (failed_attempts BETWEEN 0:::INT8 AND 3:::INT8)
);


/*********************************/
/*            OBJECTS            */
/*********************************/   

CREATE TABLE worst_models (
    -- pk
    name STRING NOT NULL,
    -- fields
    skema JSONB,
    -- audit info
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by STRING NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    updated_by STRING NULL,
    CONSTRAINT pk PRIMARY KEY (name)
);


CREATE TABLE worst_watch (
    -- pk
    id INT2 NOT NULL,
    -- fields
    ts TIMESTAMPTZ DEFAULT now() ON UPDATE now(),
    CONSTRAINT pk PRIMARY KEY (id)
);
INSERT INTO worst_watch (id) VALUES (1);



CREATE TABLE worst_events (
    object STRING,
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    username STRING,
    action STRING,
    details STRING,
    CONSTRAINT pk PRIMARY KEY (object, ts, username)
);

-- insert into models (name, skema) values ('account', '{
--     "properties": {
--         "text": {"type": "string", "default": ""},
--         "industry": {"type": "string", "default": ""},
--         "ticker": {"maxLength": 30, "type": "string", "default": ""}
--     },
--     "title": "Account",
--     "type": "object",
--     "omit_from_overview": ["text"]
-- }');

-- insert into models (name, skema) values ('opportunity', '{
--     "properties": {
--         "col0": {"type": "string", "default": ""},
--         "col1": {"maxLength": 30, "type": "string", "default": ""}
--     },
--     "title": "Opportunity",
--     "type": "object"
-- }');
