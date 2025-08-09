-- Initial database schema for ScratchBot
-- Tables: jobs, items, audits, commits, users, repos, installations

CREATE TABLE installations (
    id SERIAL PRIMARY KEY,
    github_installation_id BIGINT UNIQUE NOT NULL,
    account_login TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    github_user_id BIGINT UNIQUE NOT NULL,
    login TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE repos (
    id SERIAL PRIMARY KEY,
    github_repo_id BIGINT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    installation_id INTEGER REFERENCES installations(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE commits (
    id SERIAL PRIMARY KEY,
    repo_id INTEGER REFERENCES repos(id),
    user_id INTEGER REFERENCES users(id),
    sha TEXT UNIQUE NOT NULL,
    message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    repo_id INTEGER REFERENCES repos(id),
    user_id INTEGER REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id),
    path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audits (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id),
    action TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
