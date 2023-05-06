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

CREATE TABLE account_status(
    name STRING(20) NOT NULL,
    CONSTRAINT pk PRIMARY KEY (name)
);

INSERT INTO account_status (name) VALUES ('NEW'), ('OPPORTUNITY'), ('ENTERPRISE'), ('POC'), ('COMMERCIAL');

CREATE TABLE project_status(
    name STRING(20) NOT NULL,
    CONSTRAINT pk PRIMARY KEY (name)
);

INSERT INTO project_status (name) VALUES ('NEW'), ('OPEN'), ('IN PROGRESS'), ('ON HOLD'), ('COMPLETED');

CREATE TABLE task_status(
    name STRING(20) NOT NULL,
    CONSTRAINT pk PRIMARY KEY (name)
);

INSERT INTO task_status (name) VALUES ('NEW'), ('OPEN'), ('ON HOLD'), ('PENDING'), ('CLOSED');


CREATE TABLE accounts (
    account_id UUID NOT NULL DEFAULT gen_random_uuid(),
    name STRING NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by STRING NOT NULL,
    owned_by STRING NULL,
    due_date DATE NULL,
    text STRING NULL,
    status STRING NULL,
    data JSONB NULL,
    tags STRING [],
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    updated_by STRING NULL,
    CONSTRAINT pk PRIMARY KEY (account_id),
    CONSTRAINT status_in_status FOREIGN KEY (status)
        REFERENCES account_status(name) ON DELETE SET NULL,
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT owned_by_in_users FOREIGN KEY (owned_by)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX accounts_owned_by ON accounts(owned_by);
CREATE INVERTED INDEX accounts_data_gin ON accounts(data);
CREATE INVERTED INDEX accounts_tags_gin ON accounts(tags);

CREATE TABLE projects (
    account_id UUID NOT NULL,
    project_id UUID NOT NULL DEFAULT gen_random_uuid(),
    name STRING NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by STRING NOT NULL,
    owned_by STRING NOT NULL,
    due_date DATE NULL,
    text STRING,
    status STRING,
    data JSONB NULL,
    tags STRING [],
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    updated_by STRING NULL,
    CONSTRAINT pk PRIMARY KEY (account_id, project_id),
    CONSTRAINT status_in_status FOREIGN KEY (status)
        REFERENCES project_status(name) ON DELETE SET NULL,
    CONSTRAINT fk_accounts FOREIGN KEY (account_id) 
        REFERENCES accounts(account_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT owned_by_in_users FOREIGN KEY (owned_by)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INVERTED INDEX projects_data_gin ON projects(data);
CREATE INVERTED INDEX projects_tags_gin ON projects(tags);

CREATE TABLE tasks (
    account_id UUID NOT NULL,
    project_id UUID NOT NULL,
    task_id INT8 NOT NULL DEFAULT now()::INT8,
    name STRING NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by STRING NULL,
    owned_by STRING NOT NULL,
    due_date DATE NULL,
    text STRING,
    status STRING,
    data JSONB NULL,
    tags STRING [],
    updated_by STRING NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    CONSTRAINT pk PRIMARY KEY (account_id, project_id, task_id),
    CONSTRAINT status_in_status FOREIGN KEY (status)
        REFERENCES task_status(name) ON DELETE SET NULL,
    CONSTRAINT fk_projects FOREIGN KEY (account_id, project_id) 
        REFERENCES projects(account_id, project_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT owned_by_in_users FOREIGN KEY (owned_by)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INVERTED INDEX tasks_data_gin ON tasks(data);
CREATE INVERTED INDEX tasks_tags_gin ON tasks(tags);

CREATE TABLE notes (
    account_id UUID NOT NULL,
    project_id UUID NOT NULL,
    note_id INT8 NOT NULL DEFAULT now()::INT8,
    name STRING NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by STRING NULL,
    text STRING,
    data JSONB NULL,
    tags STRING [],
    updated_by STRING NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    CONSTRAINT pk PRIMARY KEY (account_id, project_id, note_id),
    CONSTRAINT fk_projects FOREIGN KEY (account_id, project_id) 
        REFERENCES projects(account_id, project_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INVERTED INDEX notes_data_gin ON notes(data);
CREATE INVERTED INDEX notes_tags_gin ON notes(tags);

-- INSERT INTO accounts
--     (account_id, account_name, description, tags)
--     VALUES
--     ('3f08facf-960f-41f7-99d4-02cfe45adc54', 'BOSM', 'Bank of SuperMario. Saving accounts for kids.', ARRAY['tlc', 'sh']),
--     ('97e70557-bad0-47d5-ba96-2daaf40b3840', 'Tully', 'CI/CD SaaS providing full build automation', ARRAY['saas']),
--     ('fb7e42a2-33de-442f-a194-cc295aaf93d1', 'AirMars', 'Cheap flights to Mars', ARRAY['saas', 'prom'])
-- ;

-- INSERT INTO users 
--     (user_id, full_name, email, hashed_password, is_disabled, scopes)
--     VALUES 
--     ('admin', 'admin', 'admin', '$2b$12$RP/eiWXHSSHd8BL2tm4LquEflpXWMFNrGp5hcoVrKKBzmk63IzIym', -- worst_crm
--         False, ARRAY['admin', 'rw']),
--     ('fabio', 'fabio', 'fabio', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- secret
--         False, ARRAY['rw']),
--     ('ro', 'readonly', 'ro', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- secret
--         False, ARRAY[])
-- ;
