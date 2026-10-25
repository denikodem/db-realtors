"""Сид базы данных тестовыми данными.

Запуск:
    python -m app.seed

Если в таблицах уже есть данные, сид ничего не добавляет повторно.
"""
from decimal import Decimal

from app.db import SessionLocal, init_db
from app import models


AGENTS = [
    dict(full_name="Соколова Мария Игоревна", phone="+7 (912) 555-01-01",
         email="sokolova@example.com", commission_percent=Decimal("3.00")),
    dict(full_name="Петров Алексей Николаевич", phone="+7 (912) 555-01-02",
         email="petrov@example.com", commission_percent=Decimal("2.50")),
    dict(full_name="Кузнецова Ольга Викторовна", phone="+7 (912) 555-01-03",
         email=None, commission_percent=Decimal("4.00")),
]

CLIENTS = [
    dict(full_name="Иванов Дмитрий Сергеевич", phone="+7 (921) 444-10-01",
         email="ivanov@example.com",
         notes="Ищет двухкомнатную квартиру на продажу, бюджет до 8 млн."),
    dict(full_name="Смирнова Анна Павловна", phone="+7 (921) 444-10-02",
         email="smirnova@example.com",
         notes="Хочет снять офисное помещение в центре города."),
    dict(full_name="Григорьев Иван Петрович", phone="+7 (921) 444-10-03",
         email=None,
         notes="Рассматривает загородный дом с участком."),
    dict(full_name="Фёдорова Елена Дмитриевна", phone="+7 (921) 444-10-04",
         email="fedorova@example.com",
         notes="Продаёт свою однокомнатную квартиру, просит помочь с оценкой."),
]

PROPERTIES = [
    dict(title="Двухкомнатная квартира в новом доме",
         description="Уютная квартира с современным ремонтом, закрытый двор, подземный паркинг.",
         property_type="flat", operation_type="sale",
         address="г. Екатеринбург, ул. Малышева, д. 145, кв. 27",
         district="Октябрьский", price=Decimal("7800000.00"),
         rooms=2, area=Decimal("54.30"), status="available"),
    dict(title="Однокомнатная квартира у метро",
         description="Компактная квартира в пешей доступности от станции метро, сдаётся с мебелью.",
         property_type="flat", operation_type="rent",
         address="г. Москва, Ленинский проспект, д. 34, кв. 91",
         district="Ленинский", price=Decimal("65000.00"),
         rooms=1, area=Decimal("38.00"), status="available"),
    dict(title="Трёхкомнатная квартира в центре",
         description="Просторная квартира в историческом доме, высокие потолки, вид на набережную.",
         property_type="flat", operation_type="sale",
         address="г. Казань, ул. Баумана, д. 12, кв. 5",
         district="Центральный", price=Decimal("9450000.00"),
         rooms=3, area=Decimal("78.50"), status="reserved"),
    dict(title="Загородный дом с баней",
         description="Дом из бруса 120 кв. м на участке 8 соток, гараж, скважина, магистральный газ.",
         property_type="house", operation_type="sale",
         address="Московская обл., г. Дмитров, СНТ Берёзка, уч. 14",
         district="Дмитровский", price=Decimal("12500000.00"),
         rooms=5, area=Decimal("120.00"), status="available"),
    dict(title="Коттедж для сезонного проживания",
         description="Небольшой коттедж в посёлке у леса, подходит для аренды летом.",
         property_type="house", operation_type="rent",
         address="Ленинградская обл., Всеволожский р-н, пос. Токсово, ул. Лесная, д. 7",
         district="Всеволожский", price=Decimal("85000.00"),
         rooms=4, area=Decimal("96.00"), status="available"),
    dict(title="Земельный участок под ИЖС",
         description="Ровный сухой участок с подключением к электричеству, газ по границе.",
         property_type="land", operation_type="sale",
         address="Свердловская обл., г. Верхняя Пышма, мкр. Кедровка, уч. 32",
         district="Верхнепышминский", price=Decimal("1850000.00"),
         rooms=None, area=Decimal("8.00"), status="available"),
    dict(title="Участок у озера",
         description="Участок 12 соток с выходом к озеру, тихое место для строительства дома.",
         property_type="land", operation_type="sale",
         address="Тверская обл., Калининский р-н, д. Медное, уч. 5",
         district="Калининский", price=Decimal("2400000.00"),
         rooms=None, area=Decimal("12.00"), status="archived"),
    dict(title="Офисное помещение на первой линии",
         description="Открытая планировка, отдельный вход, витринные окна, парковка для клиентов.",
         property_type="commercial", operation_type="rent",
         address="г. Новосибирск, Красный проспект, д. 100, оф. 214",
         district="Центральный", price=Decimal("150000.00"),
         rooms=None, area=Decimal("110.00"), status="available"),
    dict(title="Торговое помещение у метро",
         description="Готовый магазин с ремонтной отделкой, высокий пешеходный трафик.",
         property_type="commercial", operation_type="sale",
         address="г. Санкт-Петербург, пр. Стачек, д. 47",
         district="Кировский", price=Decimal("14900000.00"),
         rooms=None, area=Decimal("86.50"), status="reserved"),
    dict(title="Четырёхкомнатная квартира с ремонтом",
         description="Светлая квартира после капитального ремонта, два санузла, балкон и лоджия.",
         property_type="flat", operation_type="sale",
         address="г. Нижний Новгород, ул. Родионова, д. 19, кв. 12",
         district="Нижегородский", price=Decimal("11200000.00"),
         rooms=4, area=Decimal("102.40"), status="available"),
]

DEALS = [
    # (индекс объекта, индекс клиента, индекс агента)
    (2, 0, 0),   # продажа трёхкомнатной квартиры Иванову
    (1, 1, 1),   # аренда однокомнатной квартиры Смирновой
    (3, 2, 2),   # продажа загородного дома Григорьеву
]


def seed() -> None:
    db = SessionLocal()
    try:
        already = (
            db.query(models.Agent).count() > 0
            or db.query(models.Client).count() > 0
            or db.query(models.Property).count() > 0
        )
        if already:
            print("В базе уже есть данные — сид пропускается.")
            return

        agents = [models.Agent(**data) for data in AGENTS]
        clients = [models.Client(**data) for data in CLIENTS]
        db.add_all(agents)
        db.add_all(clients)
        db.flush()  # получаем id агентов и клиентов

        properties = []
        for i, data in enumerate(PROPERTIES):
            prop = models.Property(**data)
            prop.agent_id = agents[i % len(agents)].id
            properties.append(prop)
        db.add_all(properties)
        db.flush()

        deals = []
        for prop_idx, client_idx, agent_idx in DEALS:
            prop = properties[prop_idx]
            deal = models.Deal(
                property_id=prop.id,
                client_id=clients[client_idx].id,
                agent_id=agents[agent_idx].id,
                price=prop.price,
                status="completed",
            )
            deals.append(deal)
        db.add_all(deals)

        db.commit()
        print(
            f"Добавлены тестовые данные: агентов {len(agents)}, "
            f"клиентов {len(clients)}, объектов {len(properties)}, сделок {len(deals)}."
        )
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed()
