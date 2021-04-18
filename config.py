class BaseConfig:
    """Базовый класс конфига"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = "eBOCs1tn?/T2a[nb!nyY2ak0>OtM?)L/K19O7g2)Ap}{}0njGpA!>B%y#q9eh"


class DevelopmentConfig(BaseConfig):
    """Конфиг для процесса разработки"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(BaseConfig):
    """Конфиг для процесса тестирования"""
    DEBUG = True
    TESTING = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    """Конфиг для рабочего WEB приложения в продакшене"""
    pass
