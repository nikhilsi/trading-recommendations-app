-- database/migrations/001_add_authentication.sql
-- Authentication system tables migration

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    email_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMP
);

-- Create invites table
CREATE TABLE IF NOT EXISTS invites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(32) UNIQUE NOT NULL,
    email VARCHAR(255),  -- Optional: pre-assign to email
    created_by UUID REFERENCES users(id),
    used_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    notes TEXT  -- Admin can add notes about the invite
);

-- Create user sessions table (for refresh tokens)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    refresh_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP,  -- For manual session revocation
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- Create rate limiting table (for future use)
CREATE TABLE IF NOT EXISTS user_rate_limits (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(255),
    window_start TIMESTAMP,
    request_count INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, endpoint, window_start)
);

-- Create user tiers table (for future premium features)
CREATE TABLE IF NOT EXISTS user_tiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    tier VARCHAR(20) DEFAULT 'free' CHECK (tier IN ('free', 'premium', 'enterprise')),
    features JSONB DEFAULT '{}',
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create saved screener presets table (new feature)
CREATE TABLE IF NOT EXISTS screener_presets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    filters JSONB NOT NULL,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name)
);

-- Update existing tables to add user_id
ALTER TABLE watchlist ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);
ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

-- Create scan history table (track user's scanning activity)
CREATE TABLE IF NOT EXISTS scan_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scan_type VARCHAR(50),
    filters JSONB,
    results_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_invites_code ON invites(code);
CREATE INDEX IF NOT EXISTS idx_invites_expires ON invites(expires_at);
CREATE INDEX IF NOT EXISTS idx_invites_created_by ON invites(created_by);
CREATE INDEX IF NOT EXISTS idx_sessions_refresh ON user_sessions(refresh_token);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_rate_limits_user ON user_rate_limits(user_id, endpoint);
CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user ON recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_scan_history_user ON scan_history(user_id, created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_screener_presets_updated_at BEFORE UPDATE ON screener_presets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create initial admin user (you'll run this separately after setting up auth)
-- INSERT INTO users (email, password_hash, is_admin, email_verified) 
-- VALUES ('admin@example.com', '$2b$12$...', true, true);

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Authentication tables created successfully!';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Run this migration: docker-compose exec postgres psql -U trading_user -d trading_app < database/migrations/001_add_authentication.sql';
    RAISE NOTICE '2. Create initial admin user after implementing password hashing';
END $$;
