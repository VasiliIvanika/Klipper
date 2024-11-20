import time
import logging

# Логирование
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Настройка консольного логирования
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class MaterialFeed:
    def __init__(self, config):
        print("Hello world")
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.config = config

        # Чтение пинов для датчиков и подачи материала
        self.upper_sensor_pin = config.get('upper_sensor_pin')  # Пин для верхнего датчика
        self.lower_sensor_pin = config.get('lower_sensor_pin')  # Пин для нижнего датчика
        self.feed_pin = config.get('feed_pin')  # Пин для подачи материала

        # Настройка пинов
        ppins = self.printer.lookup_object('pins')
        # Используем тип 'endstop' для датчиков (входы с подтягиванием)
        self.upper_sensor = ppins.setup_pin('endstop', self.upper_sensor_pin)
        self.lower_sensor = ppins.setup_pin('endstop', self.lower_sensor_pin)
        # Используем тип 'digital_out' для подачи материала (выходной пин)
        self.feed_output = ppins.setup_pin('digital_out', self.feed_pin)

        self.feeding = False  # Флаг подачи материала

    def check_sensors(self):
        """Проверка состояния датчиков для управления подачей материала."""
        # Чтение состояния датчиков
        upper_sensor_state = self.upper_sensor['pin'].read()  # Чтение верхнего датчика
        lower_sensor_state = self.lower_sensor['pin'].read()  # Чтение нижнего датчика

        logger.debug(f"Upper sensor state: {upper_sensor_state}, Lower sensor state: {lower_sensor_state}")

        # Логика управления подачей материала
        if lower_sensor_state == 1 and not self.feeding:
            self.start_feeding()  # Если нижний датчик активен и материал не подается, начинаем подачу
        elif upper_sensor_state == 1 and self.feeding:
            self.stop_feeding()  # Если верхний датчик активен и материал подается, останавливаем подачу

    def start_feeding(self):
        """Запуск подачи материала."""
        logger.info("Starting material feed")
        self.feeding = True
        self.feed_output['pin'].write(1)  # Включение подачи материала

    def stop_feeding(self):
        """Остановка подачи материала."""
        logger.info("Stopping material feed")
        self.feeding = False
        self.feed_output['pin'].write(0)  # Остановка подачи материала

    def run(self):
        """Основной цикл проверки состояния датчиков."""
        while True:
            self.check_sensors()  # Проверка состояния датчиков
            time.sleep(0.1)  # Пауза между проверками


def load_config(config):
    """Загрузка конфигурации и создание объекта MaterialFeed."""
    return MaterialFeed(config)



