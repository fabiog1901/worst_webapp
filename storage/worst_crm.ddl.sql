USE defaultdb;

DROP DATABASE IF EXISTS worst_crm CASCADE;

CREATE DATABASE worst_crm;

USE worst_crm;

ALTER DATABASE worst_crm CONFIGURE ZONE USING 
    range_min_bytes = 134217728,
    range_max_bytes = 536870912,
    gc.ttlseconds = 600,
    num_replicas = 1,
    constraints = '[]',
    lease_preferences = '[]';


CREATE TABLE users (
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

CREATE TABLE models (
    -- pk
    name STRING NOT NULL,
    -- audit info
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by STRING NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    updated_by STRING NULL,
    -- fields
    skema JSONB,
    CONSTRAINT pk PRIMARY KEY (name),
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);


CREATE TABLE watch (
    -- pk
    id INT2 NOT NULL,
    -- fields
    ts TIMESTAMPTZ DEFAULT now() ON UPDATE now(),
    CONSTRAINT pk PRIMARY KEY (id)
);
INSERT INTO watch (id) VALUES (1);

CREATE TABLE accounts (
    -- pk
    account_id UUID NOT NULL,
    -- audit info
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by STRING NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    updated_by STRING NULL,
    -- fields not nullable
    -- fields nullable
    name STRING NULL,
    owned_by STRING NULL,
    due_date DATE NULL,
    text STRING NULL,
    status STRING(20) NULL,
    tags STRING [] NULL DEFAULT ARRAY[],
    -- not in models
    attachments STRING[] NULL DEFAULT ARRAY[],
    -- PK
    CONSTRAINT pk PRIMARY KEY (account_id),
    -- other FKs
    CONSTRAINT status_in_status FOREIGN KEY (status)
        REFERENCES account_status(name) ON DELETE SET NULL,
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT owned_by_in_users FOREIGN KEY (owned_by)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX accounts_owned_by ON accounts(owned_by);
CREATE INVERTED INDEX accounts_tags_gin ON accounts(tags);


CREATE TABLE contacts (
    -- pk
    account_id UUID NOT NULL,
    contact_id UUID NOT NULL,
    -- audit info
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by STRING NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    updated_by STRING NULL,
    -- fields not nullable
    -- fields nullable
    fname STRING NULL,
    lname STRING NULL,
    role_title STRING NULL,
    email STRING NULL,
    telephone_number STRING NULL,
    business_card STRING NULL,
    tags STRING [] NULL DEFAULT ARRAY[],
    -- PK
    CONSTRAINT pk PRIMARY KEY (account_id, contact_id),
    -- PK related FK
    CONSTRAINT fk_accounts FOREIGN KEY (account_id) 
        REFERENCES accounts(account_id) ON DELETE CASCADE ON UPDATE CASCADE,
    -- other FKs
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);



CREATE TABLE events (
    object STRING,
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    username STRING,
    action STRING,
    details STRING,
    CONSTRAINT pk PRIMARY KEY (object, ts, username)
);
