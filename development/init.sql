-- Types
CREATE TYPE permission AS ENUM (
    'customers:create',
    'customers:read',
    'customers:update',
    'customers:delete',
    'favorites:create',
    'favorites:read',
    'favorites:update',
    'favorites:delete'
);

-- Tables
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    slug VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    permissions permission[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT "uq_users_slug" UNIQUE (slug)
);
CREATE INDEX IF NOT EXISTS "idx_users_permissions_gin"
    ON users USING GIN (permissions);

CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT "uq_customers_email" UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS products_cache (
    id BIGINT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    image_url TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    review_rate DECIMAL(10, 2) NOT NULL,
    review_count INT NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL,
    soft_ttl INTERVAL NOT NULL DEFAULT '5 minutes',
    hard_ttl INTERVAL NOT NULL DEFAULT '30 minutes'
);

CREATE TABLE IF NOT EXISTS customer_favorite_products (
    customer_id UUID NOT NULL,
    product_id BIGINT NOT NULL,
    favorited_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (customer_id, product_id),
    CONSTRAINT "fk_customerfavoriteproducts_customer"
        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);
