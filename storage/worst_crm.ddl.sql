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

CREATE TABLE accounts (
    account_id UUID NOT NULL DEFAULT gen_random_uuid(),
    account_name STRING NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    description STRING,
    tags STRING [],
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    CONSTRAINT pk PRIMARY KEY (account_id)
);

CREATE TABLE projects (
    account_id UUID NOT NULL,
    project_id UUID NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    description STRING,
    project_name STRING NOT NULL,
    status STRING,
    tags STRING [],
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    CONSTRAINT pk PRIMARY KEY (account_id, project_id),
    CONSTRAINT fk_accounts FOREIGN KEY (account_id) 
        REFERENCES accounts(account_id) ON DELETE CASCADE
);

CREATE TABLE notes (
    account_id UUID NOT NULL,
    project_id UUID NOT NULL,
    note_id INT8 NOT NULL DEFAULT now()::INT8,
    note_name STRING NOT NULL,
    content STRING,
    tags STRING [],
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    CONSTRAINT pk PRIMARY KEY (account_id, project_id, note_id),
    CONSTRAINT fk_projects FOREIGN KEY (account_id, project_id) 
        REFERENCES projects(account_id, project_id) ON DELETE CASCADE
);

CREATE TABLE tasks (
    account_id UUID NOT NULL,
    project_id UUID NOT NULL,
    task_id INT8 NOT NULL DEFAULT now()::INT8,
    task_name STRING NOT NULL,
    content STRING,
    task_status STRING,
    tags STRING [],
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    CONSTRAINT pk PRIMARY KEY (account_id, project_id, task_id),
    CONSTRAINT fk_projects FOREIGN KEY (account_id, project_id) 
        REFERENCES projects(account_id, project_id) ON DELETE CASCADE
);

CREATE TABLE users (
    username string not null,
    full_name string,
    email string,
    hashed_password string,
    is_disabled bool,
    scopes string[],
    CONSTRAINT pk PRIMARY KEY (username)
);

INSERT INTO accounts
    (account_id, account_name, description, tags)
    VALUES
    ('3f08facf-960f-41f7-99d4-02cfe45adc54', 'BOSM', 'Bank of SuperMario. Saving accounts for kids.', ARRAY['tlc', 'sh']),
    ('97e70557-bad0-47d5-ba96-2daaf40b3840', 'Tully', 'CI/CD SaaS providing full build automation', ARRAY['saas']),
    ('fb7e42a2-33de-442f-a194-cc295aaf93d1', 'AirMars', 'Cheap flights to Mars', ARRAY['saas', 'prom'])
;

INSERT INTO users 
    (username, full_name, email, hashed_password, is_disabled, scopes)
    VALUES 
    ('admin', 'admin', 'admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- secret
        False, ARRAY['admin', 'rw']),
    ('fabio', 'fabio', 'fabio', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- secret
        False, ARRAY['rw']),
    ('ro', 'readonly', 'ro', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- secret
        False, ARRAY[])
;
