-- Add API idempotency support without changing starter tables.

CREATE TABLE IF NOT EXISTS payment_requests (
    idempotency_key VARCHAR(128) PRIMARY KEY,
    fingerprint CHAR(64) NOT NULL,
    transaction_id BIGINT NOT NULL UNIQUE
        REFERENCES transactions(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Local Linux peer-authenticated application user.
SELECT format('CREATE ROLE %I LOGIN', :'app_user')
WHERE NOT EXISTS (
    SELECT 1 FROM pg_roles WHERE rolname = :'app_user'
)
\gexec

GRANT CONNECT ON DATABASE minipay TO :"app_user";
GRANT USAGE ON SCHEMA public TO :"app_user";

GRANT SELECT, INSERT ON
    customers, transactions, callbacks, payment_requests
TO :"app_user";

GRANT USAGE, SELECT ON ALL SEQUENCES
IN SCHEMA public TO :"app_user";
