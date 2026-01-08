label_vin = "Введіть vin код авто"

SERVICE_NAME_TRANSLATIONS = {
    "engine_oil_and_filter": "Заміна моторного масла та масляного фільтра",
    "gas_filter": "Заміна фільтра газової системи",
    "engine_air_filter": "Заміна повітряного фільтра двигуна",
    "cabin_filter": "Заміна салонного фільтра (рекомендується вугільний фільтр)",
    "suspension_check": "Перевірка стану підвіски",
    "brake_fluid": "Заміна гальмівної рідини",
    "brake_pads": "Заміна гальмівних колодок",
    "electrical_and_engine_check": "Перевірка електросистеми та компонентів двигуна",
    "power_steering_fluid": "Заміна рідини гідропідсилювача керма",
    "coolant": "Заміна охолоджуючої рідини (двигун та інвертор)",
    "coolant_pump": "Заміна насоса охолодження (двигун та інвертор)",
    "gearbox_oil": "Заміна масла коробки передач",
    "fuel_filter": "Заміна паливного фільтра",
}

SERVICE_NAME_TO_KEY = {
    "Заміна моторного масла та масляного фільтра": "engine_oil_and_filter",
    "Заміна фільтра газової системи": "gas_filter",
    "Заміна повітряного фільтра двигуна": "engine_air_filter",
    "Заміна салонного фільтра (рекомендується вугільний фільтр)": "cabin_filter",
    "Перевірка стану підвіски": "suspension_check",
    "Заміна гальмівної рідини": "brake_fluid",
    "Заміна гальмівних колодок": "brake_pads",
    "Перевірка електросистеми та компонентів двигуна": "electrical_and_engine_check",
    "Заміна рідини гідропідсилювача керма": "power_steering_fluid",
    "Заміна охолоджуючої рідини (двигун та інвертор)": "coolant",
    "Заміна насоса охолодження (двигун та інвертор)": "coolant_pump",
    "Заміна масла коробки передач": "gearbox_oil",
    "Заміна паливного фільтра": "fuel_filter",
}

# Дефолтна схема сервісу
DEFAULT_SERVICE_SCHEMA = {
    "regulation_name": "СИНХРОНІЗОВАНИЙ РЕГЛАМЕНТ ОБСЛУГОВУВАННЯ",
    "current_mileage_km": 0,
    "services": [
        {
            "key": "engine_oil_and_filter",
            "name": "Заміна моторного масла та масляного фільтра",
            "interval_km": 10000,
            "last_service_km": 0
        },
        {
            "key": "gas_filter",
            "name": "Заміна фільтра газової системи",
            "interval_km": 10000,
            "last_service_km": 0
        },
        {
            "key": "engine_air_filter",
            "name": "Заміна повітряного фільтра двигуна",
            "interval_km": 20000,
            "last_service_km": 0
        },
        {
            "key": "cabin_filter",
            "name": "Заміна салонного фільтра (рекомендується вугільний фільтр)",
            "interval_km": 20000,
            "last_service_km": 0
        },
        {
            "key": "suspension_check",
            "name": "Перевірка стану підвіски",
            "interval_km": 20000,
            "last_service_km": 0
        },
        {
            "key": "brake_fluid",
            "name": "Заміна гальмівної рідини",
            "interval_km": 30000,
            "last_service_km": 0
        },
        {
            "key": "brake_pads",
            "name": "Заміна гальмівних колодок",
            "interval_km": 30000,
            "last_service_km": 0
        },
        {
            "key": "electrical_and_engine_check",
            "name": "Перевірка електросистеми та компонентів двигуна",
            "interval_km": 20000,
            "last_service_km": 0
        },
        {
            "key": "power_steering_fluid",
            "name": "Заміна рідини гідропідсилювача керма",
            "interval_km": 48000,
            "last_service_km": 0
        },
        {
            "key": "coolant",
            "name": "Заміна охолоджуючої рідини (двигун та інвертор)",
            "interval_km": 60000,
            "last_service_km": 0
        },
        {
            "key": "coolant_pump",
            "name": "Заміна насоса охолодження (двигун та інвертор)",
            "interval_km": 120000,
            "last_service_km": 0
        },
        {
            "key": "gearbox_oil",
            "name": "Заміна масла коробки передач",
            "interval_km": 72000,
            "last_service_km": 0
        },
        {
            "key": "fuel_filter",
            "name": "Заміна паливного фільтра",
            "interval_km": 72000,
            "last_service_km": 0
        }
    ]
}

# Тестова схема (для зворотної сумісності)
test_schema_service = {
    "regulation_name": "SYNCHRONIZED SERVICE REGULATION",
    "current_mileage_km": 162467,
    "services": [
        {
            "key": "engine_oil_and_filter",
            "name": "Engine oil and oil filter replacement",
            "interval_km": 10000,
            "last_service_km": 162467
        },
        {
            "key": "gas_filter",
            "name": "Gas system filter replacement",
            "interval_km": 10000,
            "last_service_km": 162467
        },
        {
            "key": "engine_air_filter",
            "name": "Engine air filter replacement",
            "interval_km": 20000,
            "last_service_km": 162467
        },
        {
            "key": "cabin_filter",
            "name": "Cabin filter replacement (carbon filter recommended)",
            "interval_km": 20000,
            "last_service_km": 162467
        },
        {
            "key": "suspension_check",
            "name": "Suspension condition check",
            "interval_km": 20000,
            "last_service_km": 162467
        },
        {
            "key": "brake_fluid",
            "name": "Brake fluid replacement",
            "interval_km": 30000,
            "last_service_km": 162467
        },
        {
            "key": "brake_pads",
            "name": "Brake pads replacement",
            "interval_km": 30000,
            "last_service_km": 162467
        },
        {
            "key": "electrical_and_engine_check",
            "name": "Electrical system and engine components check",
            "interval_km": 20000,
            "last_service_km": 162467
        },
        {
            "key": "power_steering_fluid",
            "name": "Power steering fluid replacement",
            "interval_km": 48000,
            "last_service_km": 0
        },
        {
            "key": "coolant",
            "name": "Coolant replacement (engine and inverter)",
            "interval_km": 60000,
            "last_service_km": 112467
        },
        {
            "key": "coolant_pump",
            "name": "Coolant pump replacement (engine and inverter)",
            "interval_km": 120000,
            "last_service_km": 0
        },
        {
            "key": "gearbox_oil",
            "name": "Gearbox oil replacement",
            "interval_km": 72000,
            "last_service_km": 162467
        },
        {
            "key": "fuel_filter",
            "name": "Fuel filter replacement",
            "interval_km": 72000,
            "last_service_km": 0
        }
    ]
}
