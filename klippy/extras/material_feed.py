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

        # Determine start and shutdown values for upper pin
        self.upper_sensor.last_value = config.getfloat(
            'value_upper', 0., minval=0., maxval=1.)
        self.upper_sensor.shutdown_value = config.getfloat(
            'shutdown_value_upper', 0., minval=0., maxval=1.)
        # Determine start and shutdown values for lower pin
        self.lower_sensor.last_value = config.getfloat(
            'value_lower', 0., minval=0., maxval=1.)
        self.lower_sensor.shutdown_value = config.getfloat(
            'shutdown_value_lower', 0., minval=0., maxval=1.)
        # Determine start and shutdown values for feed output pin
        self.feed_output.last_value = config.getfloat(
            'value_feed', 0., minval=0., maxval=1.)
        self.feed_output.shutdown_value = config.getfloat(
            'shutdown_value_feed', 0., minval=0., maxval=1.)

    def check_sensors(self):
        """Проверка состояния датчиков для управления подачей материала."""
        # Чтение состояния датчиков
        upper_sensor_state = self.upper_sensor.last_value
        lower_sensor_state = self.lower_sensor.last_value
        feed_output_state = self.feed_output.last_value
        logger.debug(
            f"Upper sensor state: {upper_sensor_state},"
            f" Lower sensor state: {lower_sensor_state},"
            f" Feed output state: {feed_output_state}"
        )

        # Логика управления подачей материала
        if lower_sensor_state == 1 and not feed_output_state:
            self.start_feeding()  # Если нижний датчик активен и материал не подается, начинаем подачу
        elif upper_sensor_state == 1 and feed_output_state:
            self.stop_feeding()  # Если верхний датчик активен и материал подается, останавливаем подачу

    def start_feeding(self):
        """Запуск подачи материала."""
        logger.info("Starting material feed")
        self.feed_output.last_value = 1

    def stop_feeding(self):
        """Остановка подачи материала."""
        logger.info("Stopping material feed")
        self.feed_output.last_value = 0

    def run(self):
        """Основной цикл проверки состояния датчиков."""
        while True:
            self.check_sensors()  # Проверка состояния датчиков
            time.sleep(0.1)  # Пауза между проверками


def load_config(config):
    """Загрузка конфигурации и создание объекта MaterialFeed."""
    return MaterialFeed(config)




