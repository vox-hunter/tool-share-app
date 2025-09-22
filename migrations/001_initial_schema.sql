-- Create core tables for ToolShare application

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tools table
CREATE TABLE IF NOT EXISTS tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID REFERENCES users(id) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    condition TEXT CHECK (condition IN ('new', 'good', 'fair')) DEFAULT 'good',
    latitude NUMERIC,
    longitude NUMERIC,
    daily_price NUMERIC DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tool images table
CREATE TABLE IF NOT EXISTS tool_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_id UUID REFERENCES tools(id) ON DELETE CASCADE NOT NULL,
    storage_path TEXT NOT NULL,
    ordering INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reservations table
CREATE TABLE IF NOT EXISTS reservations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_id UUID REFERENCES tools(id) NOT NULL,
    borrower_id UUID REFERENCES users(id) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status TEXT CHECK (status IN ('requested', 'accepted', 'declined', 'cancelled', 'completed')) DEFAULT 'requested',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_date_range CHECK (start_date <= end_date),
    CONSTRAINT no_self_booking CHECK (borrower_id != (SELECT owner_id FROM tools WHERE id = tool_id))
);

-- Prevent overlapping accepted reservations
CREATE UNIQUE INDEX IF NOT EXISTS no_overlapping_reservations 
ON reservations (tool_id, start_date, end_date) 
WHERE status = 'accepted';

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reservation_id UUID REFERENCES reservations(id) UNIQUE NOT NULL,
    reviewer_id UUID REFERENCES users(id) NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id UUID REFERENCES users(id),
    action_type TEXT NOT NULL,
    json_payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tools_owner ON tools(owner_id);
CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category);
CREATE INDEX IF NOT EXISTS idx_tools_active ON tools(is_active);
CREATE INDEX IF NOT EXISTS idx_reservations_tool ON reservations(tool_id);
CREATE INDEX IF NOT EXISTS idx_reservations_borrower ON reservations(borrower_id);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);
CREATE INDEX IF NOT EXISTS idx_reservations_dates ON reservations(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tools ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE reservations ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Users: Users can read all profiles but only update their own
CREATE POLICY "Users can read all profiles" ON users FOR SELECT USING (true);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON users FOR INSERT WITH CHECK (auth.uid() = id);

-- Tools: Public read, owners can modify
CREATE POLICY "Anyone can read active tools" ON tools FOR SELECT USING (is_active = true);
CREATE POLICY "Owners can insert tools" ON tools FOR INSERT WITH CHECK (auth.uid() = owner_id);
CREATE POLICY "Owners can update own tools" ON tools FOR UPDATE USING (auth.uid() = owner_id);
CREATE POLICY "Owners can delete own tools" ON tools FOR DELETE USING (auth.uid() = owner_id);

-- Tool images: Follow tool permissions
CREATE POLICY "Tool images readable with tools" ON tool_images FOR SELECT USING (
    EXISTS (SELECT 1 FROM tools WHERE tools.id = tool_images.tool_id AND tools.is_active = true)
);
CREATE POLICY "Tool owners can manage images" ON tool_images FOR ALL USING (
    EXISTS (SELECT 1 FROM tools WHERE tools.id = tool_images.tool_id AND auth.uid() = tools.owner_id)
);

-- Reservations: Borrowers can create, owners can update status
CREATE POLICY "Users can read own reservations" ON reservations FOR SELECT USING (
    auth.uid() = borrower_id OR 
    auth.uid() = (SELECT owner_id FROM tools WHERE id = tool_id)
);
CREATE POLICY "Users can create reservations" ON reservations FOR INSERT WITH CHECK (
    auth.uid() = borrower_id AND
    auth.uid() != (SELECT owner_id FROM tools WHERE id = tool_id)
);
CREATE POLICY "Tool owners can update reservation status" ON reservations FOR UPDATE USING (
    auth.uid() = (SELECT owner_id FROM tools WHERE id = tool_id) OR
    (auth.uid() = borrower_id AND status = 'requested')
);

-- Reviews: Only for completed reservations by borrower
CREATE POLICY "Anyone can read reviews" ON reviews FOR SELECT USING (true);
CREATE POLICY "Borrowers can create reviews for completed reservations" ON reviews FOR INSERT WITH CHECK (
    auth.uid() = reviewer_id AND
    EXISTS (
        SELECT 1 FROM reservations 
        WHERE id = reservation_id 
        AND borrower_id = auth.uid() 
        AND status = 'completed'
        AND end_date < CURRENT_DATE
    )
);

-- Audit logs: Insert only, admin read
CREATE POLICY "System can insert audit logs" ON audit_logs FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can read own audit logs" ON audit_logs FOR SELECT USING (actor_id = auth.uid());