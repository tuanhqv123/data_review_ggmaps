-- PostgreSQL schema for places and reviews data
-- Based on places.json structure

-- Create place table
CREATE TABLE place (
    id SERIAL PRIMARY KEY,
    url TEXT,
    name VARCHAR(255),
    rating DECIMAL(3,1),
    review_count INTEGER,
    address TEXT,
    website TEXT,
    phone VARCHAR(50),
    business_hours JSONB, -- Store business hours as JSON object
    accessibility TEXT[], -- Array of accessibility options
    service_options TEXT[], -- Array of service options
    highlights TEXT[], -- Array of highlights
    popular_for TEXT[], -- Array of what it's popular for
    offerings TEXT[], -- Array of offerings
    dining_options TEXT[], -- Array of dining options
    amenities TEXT[], -- Array of amenities
    atmosphere TEXT[], -- Array of atmosphere descriptions
    crowd TEXT[], -- Array of crowd descriptions
    planning TEXT[], -- Array of planning information
    payments TEXT[], -- Array of payment methods
    children TEXT[], -- Array of children-related info
    parking TEXT[], -- Array of parking options
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create review table
CREATE TABLE review (
    id SERIAL PRIMARY KEY,
    place_id INTEGER REFERENCES place(id) ON DELETE CASCADE,
    review_id VARCHAR(255) UNIQUE,
    reviewer_name VARCHAR(255),
    reviewer_profile_url TEXT,
    rating DECIMAL(3,1),
    time VARCHAR(100), -- Store as string since it's relative time like "2 tháng trước"
    time_datetime TIMESTAMP, -- Store actual datetime calculated from relative time
    text TEXT,
    owner_response TEXT,
    review_details JSONB, -- Store review details as JSON object
    photos TEXT[], -- Array of photo URLs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);