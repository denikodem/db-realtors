-- Учебные SQL-запросы к базе данных риелторского сайта.

-- 1. Список объектов недвижимости с именем агента.
SELECT p.id, p.title, p.address, p.price, p.status, a.full_name AS agent_name
FROM properties p
JOIN agents a ON a.id = p.agent_id
ORDER BY p.created_at DESC;

-- 2. Доступные объекты в конкретном районе.
SELECT id, title, address, price
FROM properties
WHERE status = 'available' AND district = 'Центральный';

-- 3. Объекты на продажу с ценой ниже определённой суммы.
SELECT id, title, property_type, price
FROM properties
WHERE operation_type = 'sale' AND price < 8000000
ORDER BY price;

-- 4. Сделки с названием объекта, клиентом и агентом.
SELECT d.id, d.deal_date, d.price, d.status,
       p.title AS property_title,
       c.full_name AS client_name,
       a.full_name AS agent_name
FROM deals d
JOIN properties p ON p.id = d.property_id
JOIN clients c ON c.id = d.client_id
JOIN agents a ON a.id = d.agent_id
ORDER BY d.deal_date DESC;

-- 5. Количество объектов по статусу.
SELECT status, COUNT(*) AS cnt
FROM properties
GROUP BY status
ORDER BY cnt DESC;

-- 6. Сумма завершённых сделок по каждому агенту.
SELECT a.full_name, SUM(d.price) AS total_price, COUNT(d.id) AS deals_count
FROM agents a
LEFT JOIN deals d ON d.agent_id = a.id AND d.status = 'completed'
GROUP BY a.id, a.full_name
ORDER BY total_price DESC NULLS LAST;

-- 7. Клиенты и количество их сделок.
SELECT c.full_name, c.phone, COUNT(d.id) AS deals_count
FROM clients c
LEFT JOIN deals d ON d.client_id = c.id
GROUP BY c.id, c.full_name, c.phone
ORDER BY deals_count DESC;

-- 8. Средний ценник за квадратный метр по типам объектов (продажа).
SELECT property_type, ROUND(AVG(price / NULLIF(area, 0)), 2) AS avg_price_per_sqm
FROM properties
WHERE operation_type = 'sale' AND area IS NOT NULL AND area > 0
GROUP BY property_type;
