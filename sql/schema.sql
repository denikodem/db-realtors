-- Схема базы данных учебного проекта "Риелторские услуги".
-- Эквивалентна моделям SQLAlchemy (app/models.py).

CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(150) UNIQUE,
    commission_percent NUMERIC(5, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_agents_commission CHECK (commission_percent >= 0 AND commission_percent <= 100)
);

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(150) UNIQUE,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    property_type VARCHAR(20) NOT NULL,
    operation_type VARCHAR(10) NOT NULL,
    address VARCHAR(250) NOT NULL,
    district VARCHAR(100),
    price NUMERIC(12, 2) NOT NULL,
    rooms INTEGER,
    area NUMERIC(8, 2),
    status VARCHAR(20) NOT NULL DEFAULT 'available',
    agent_id INTEGER NOT NULL REFERENCES agents (id) ON DELETE RESTRICT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_properties_property_type CHECK (property_type IN ('flat', 'house', 'land', 'commercial')),
    CONSTRAINT ck_properties_operation_type CHECK (operation_type IN ('sale', 'rent')),
    CONSTRAINT ck_properties_status CHECK (status IN ('available', 'reserved', 'archived')),
    CONSTRAINT ck_properties_price CHECK (price >= 0),
    CONSTRAINT ck_properties_rooms CHECK (rooms >= 0),
    CONSTRAINT ck_properties_area CHECK (area >= 0)
);

CREATE TABLE deals (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties (id) ON DELETE RESTRICT,
    client_id INTEGER NOT NULL REFERENCES clients (id) ON DELETE RESTRICT,
    agent_id INTEGER NOT NULL REFERENCES agents (id) ON DELETE RESTRICT,
    deal_date DATE NOT NULL DEFAULT CURRENT_DATE,
    price NUMERIC(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_deals_status CHECK (status IN ('draft', 'completed', 'cancelled')),
    CONSTRAINT ck_deals_price CHECK (price >= 0)
);

-- Индексы
CREATE INDEX ix_properties_status ON properties (status);
CREATE INDEX ix_properties_district ON properties (district);
CREATE INDEX ix_properties_price ON properties (price);
CREATE INDEX ix_properties_agent_id ON properties (agent_id);
CREATE INDEX ix_deals_property_id ON deals (property_id);
CREATE INDEX ix_deals_client_id ON deals (client_id);
CREATE INDEX ix_deals_agent_id ON deals (agent_id);
