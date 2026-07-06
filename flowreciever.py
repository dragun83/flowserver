import socket
import logging
import asyncio
import netflow
import datetime
from netflow import v9




class NetFlowV9Listener:
    """
    Класс сборщика данных NetFlow
    Параметры:
    ip_addr - Адрес на котрый "прибивается" слушатель
    port - UDP порт
    """
    def __init__(self,ip_addr:str = "0.0.0.0", port:int = 2055):
        self.__port = port
        self.__ip_addr = ip_addr
        self.__log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.__soc = None
        self.__parser_templ = {"netflow":{}, "ipfix":{}}
        self.__dataset_buffer = {}
        self.__dataset_max_buf_size = 20000

    def  start(self):
        """
        Запускаем слушатель.
        """
        self.__log.info(f"Запускаем сервер на адресе: {self.__ip_addr}, порт: {self.__port}")
        self.__soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__soc.bind((self.__ip_addr, self.__port))
        loop = asyncio.get_event_loop()

    def parse_packet(self, packet:bytes, src_ip:str):
        """
        Метод парсит пакет NetFlow
        Вызывается при получени пакета асингхронным слушателем. Возвращает содержимое пакета, если есть шаблон, пополняет справочник шаблонов,
        если пришел шаблон или возвращает None  если шаблона нет и он не пришел.
        На вход принимает байты пакетов, источник пакета
        """
        try:
            netflow_data = netflow.parse_packet(packet,self.__parser_templ)
            self.__log.debug(f"Получили пакет от {src_ip}, содержимое {netflow_data.flows}")
            return netflow_data
        except v9.V9TemplateNotRecognized:
             self.__log.warning(f"Не удалось распарсить пакет от {src_ip}. Не обнаружен шаблон. Продолжаем")
             return None


    def stop(self):
        self.__log.info("Останавливаем сервер.")
        if self.__soc != None:
            self.__soc.close
            self.__soc = None
        else:
            pass

    def get_sock(self):
        return self.__soc

def print_all_records(flowset:list):
    """
    Тестовая функция печатает все данные в удобном формате
    На вход получаем список словарей flowset
    """
    print(f"Длинна flowset: {len(flowset)}\n" )
    for datarecord in flowset:
#        print(f"Содержание datarecord:  {datarecord.data.keys()}\n")
        print(f"Содержание datarecord:  {datarecord}\n")


def main_test(address:str, port:int):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((address, port))
    v9_templ = {"netflow":{}, "ipfix":{}}
    try:
        while True:
            data, src_ip = s.recvfrom(4096)
            if data:
                try:
                    net_flow_data = netflow.parse_packet(data,v9_templ)
                    print_all_records(net_flow_data.flows)
                except v9.V9TemplateNotRecognized:
                    print(f"Не удалось получить \033[9mпакет с пакетами\033[0m шаблон. Продолжаем.")
                    continue
                except Exception as e:
                    print(f"Падаем с ошибкой {e}")
    except Exception:
        s.close()
        print(f"Stop!")

def main_class_test():
    # Настроем логирование. Тут можно покрутить формат вывода данных - для этого все уже есть.
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    log_handler = logging.StreamHandler()
    root_logger.addHandler(log_handler)
    root_logger.setLevel(logging.INFO)

    listener = NetFlowV9Listener()
    listener.start()
    lnr_soc = listener.get_sock()
    while True:
        data, src_ip = lnr_soc.recvfrom(4096)
        if data:
            netflow_data = listener.parse_packet(data, str(src_ip))
            if netflow_data != None:
                print(f"Класс вроде как работает. Получили {netflow_data.header.source_id}. Там содержатся данные {netflow_data.flows}")


if __name__ == "__main__":
    #main_test("0.0.0.0", 2055)
    main_class_test()
