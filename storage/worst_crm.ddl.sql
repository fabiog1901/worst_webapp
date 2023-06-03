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
/*            STATUSES           */
/*********************************/   
CREATE TABLE account_status(
    name STRING(20) NOT NULL,
    CONSTRAINT pk PRIMARY KEY (name)
);

INSERT INTO account_status (name) VALUES ('NEW'), ('OPPORTUNITY'), ('ENTERPRISE'), ('POC'), ('COMMERCIAL');


CREATE TABLE opportunity_status(
    name STRING(20) NOT NULL,
    CONSTRAINT pk PRIMARY KEY (name)
);

INSERT INTO opportunity_status (name) VALUES ('NEW'), ('OPEN'), ('IN PROGRESS'), ('ON HOLD'), ('COMPLETED');


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


/*********************************/
/*            OBJECTS            */
/*********************************/   
CREATE TABLE accounts (
    -- pk
    account_id UUID NOT NULL DEFAULT gen_random_uuid(),
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



CREATE TABLE opportunities (
    -- pk
    account_id UUID NOT NULL,
    opportunity_id UUID NOT NULL DEFAULT gen_random_uuid(),
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
    CONSTRAINT pk PRIMARY KEY (account_id, opportunity_id),
    -- PK related FK
    CONSTRAINT fk_accounts FOREIGN KEY (account_id) 
        REFERENCES accounts(account_id) ON DELETE CASCADE ON UPDATE CASCADE,
    -- other FKs
    CONSTRAINT status_in_status FOREIGN KEY (status)
        REFERENCES opportunity_status(name) ON DELETE SET NULL,
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT owned_by_in_users FOREIGN KEY (owned_by)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INVERTED INDEX opportunity_tags_gin ON opportunities(tags);


CREATE TABLE projects (
    -- pk
    account_id UUID NOT NULL,
    opportunity_id UUID NOT NULL,
    project_id UUID NOT NULL DEFAULT gen_random_uuid(),
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
    CONSTRAINT pk PRIMARY KEY (account_id, opportunity_id, project_id),
    -- PK related FK
    CONSTRAINT fk_opportunities FOREIGN KEY (account_id, opportunity_id) 
        REFERENCES opportunities(account_id, opportunity_id) ON DELETE CASCADE ON UPDATE CASCADE,
    -- other FKs
    CONSTRAINT status_in_status FOREIGN KEY (status)
        REFERENCES project_status(name) ON DELETE SET NULL,
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT owned_by_in_users FOREIGN KEY (owned_by)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INVERTED INDEX projects_tags_gin ON projects(tags);


CREATE TABLE tasks (
    -- pk
    account_id UUID NOT NULL,
    opportunity_id UUID NOT NULL,
    project_id UUID NOT NULL,
    task_id UUID NOT NULL DEFAULT gen_random_uuid(),
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
    CONSTRAINT pk PRIMARY KEY (account_id, opportunity_id, project_id, task_id),
    -- PK related FK
    CONSTRAINT fk_projects FOREIGN KEY (account_id, opportunity_id, project_id) 
        REFERENCES projects(account_id, opportunity_id, project_id) ON DELETE CASCADE ON UPDATE CASCADE,
    -- other FKs
    CONSTRAINT status_in_status FOREIGN KEY (status)
        REFERENCES task_status(name) ON DELETE SET NULL,
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT owned_by_in_users FOREIGN KEY (owned_by)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INVERTED INDEX tasks_tags_gin ON tasks(tags);


CREATE TABLE account_notes (
    -- pk
    account_id UUID NOT NULL,
    note_id UUID NOT NULL DEFAULT gen_random_uuid(),
    -- audit info
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by STRING NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    updated_by STRING NULL,
    -- fields not nullable
    -- fields nullable
    name STRING NULL,
    text STRING NULL,
    tags STRING [] NULL DEFAULT ARRAY[],
    -- not in models
    attachments STRING[] NULL DEFAULT ARRAY[],
    -- PK
    CONSTRAINT pk PRIMARY KEY (account_id, note_id),
    -- PK related FK
    CONSTRAINT fk_accounts FOREIGN KEY (account_id) 
        REFERENCES accounts(account_id) ON DELETE CASCADE ON UPDATE CASCADE,
    -- other FKs
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INVERTED INDEX account_notes_tags_gin ON account_notes(tags);


CREATE TABLE opportunity_notes (
    -- pk
    account_id UUID NOT NULL,
    opportunity_id UUID NOT NULL,
    note_id UUID NOT NULL DEFAULT gen_random_uuid(),
    -- audit info
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by STRING NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    updated_by STRING NULL,
    -- fields not nullable
    -- fields nullable
    name STRING NULL,
    text STRING NULL,
    tags STRING [] NULL DEFAULT ARRAY[],
    -- not in models
    attachments STRING[] NULL DEFAULT ARRAY[],
    -- PK
    CONSTRAINT pk PRIMARY KEY (account_id, opportunity_id, note_id),
    -- FK
    CONSTRAINT fk_opportunities FOREIGN KEY (account_id, opportunity_id) 
        REFERENCES opportunities(account_id, opportunity_id) ON DELETE CASCADE ON UPDATE CASCADE,
    -- PK related FKs
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INVERTED INDEX opportunity_notes_tags_gin ON opportunity_notes(tags);


CREATE TABLE project_notes (
    -- pk
    account_id UUID NOT NULL,
    opportunity_id UUID NOT NULL,
    project_id UUID NOT NULL,
    note_id UUID NOT NULL DEFAULT gen_random_uuid(),
    -- audit info
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by STRING NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    updated_by STRING NULL,
    -- fields not nullable
    -- fields nullable
    name STRING NULL,
    text STRING NULL,
    tags STRING [] NULL DEFAULT ARRAY[],
    -- not in models
    attachments STRING[] NULL DEFAULT ARRAY[],
    -- PK
    CONSTRAINT pk PRIMARY KEY (account_id, opportunity_id, project_id, note_id),
    -- PK related FK
    CONSTRAINT fk_projects FOREIGN KEY (account_id, opportunity_id, project_id) 
        REFERENCES projects(account_id, opportunity_id, project_id) ON DELETE CASCADE ON UPDATE CASCADE,
    -- other FKs
    CONSTRAINT created_by_in_users FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT updated_by_in_users FOREIGN KEY (updated_by)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INVERTED INDEX project_notes_tags_gin ON project_notes(tags);



