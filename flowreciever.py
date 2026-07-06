import socket
import logging
import asyncio
import netflow
from netflow import v9

#TODO  Починить остановку. сейчас падает с ошибкой.



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
        self.__udp_buf_size = 4096
        self.__log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.__soc = None
        self.__parser_templ = {"netflow":{}, "ipfix":{}}
        self.__dataset_buffer = []
        self.__dataset_max_buf_size = 2000
        self.__is_running = False

    async def start(self):
        """
        Запускаем слушатель.
        """
        self.__log.info(f"Запускаем сервер на адресе: {self.__ip_addr}, порт: {self.__port}")
        self.__soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__soc.bind((self.__ip_addr, self.__port))
        self.__is_running = True

    async def listen(self):
        loop = asyncio.get_event_loop()

        while self.__is_running:
            try:
                data, src_ip = await loop.sock_recvfrom(self.__soc, self.__udp_buf_size)
                if data:
                    net_flow_data = await self.parse_packet(data, str(src_ip))
                    if len(self.__dataset_buffer) < self.__dataset_max_buf_size and net_flow_data != None:
                        self.__dataset_buffer.append(net_flow_data)
                        self.__log.debug(f"Записали dataset  в буфер. Размер буфера {len(self.__dataset_buffer)}")
                    elif net_flow_data != None:
                        self.__dataset_buffer.pop(0)
                        self.__dataset_buffer.append(net_flow_data)
                        self.__log.debug(f"Записали dataset  в буфер и удалили 1 старую запись. Размер буфера {len(self.__dataset_buffer)}")
                    else:
                        self.__log.debug(f"Получен пустой пакет - пропускаем. В буфер не кладем. Размер {len(self.__dataset_buffer)}")
                        pass
            except socket.error as e:
                self.__log.error(f" Ошибка сокета {e}")
                break
            except Exception as e:
                self.__log.warning(f"Неожиданная ошибка {e}")

    async def parse_packet(self, packet:bytes, src_ip:str):
        """
        Метод парсит пакет NetFlow
        Вызывается при получени пакета асингхронным слушателем. Возвращает содержимое пакета, если есть шаблон, пополняет справочник шаблонов,
        если пришел шаблон или возвращает None  если шаблона нет и он не пришел.
        На вход принимает байты пакетов, источник пакета
        """
        try:
            netflow_data = netflow.parse_packet(packet,self.__parser_templ)
            self.__log.debug(f"Получили пакет от {src_ip}, содержимое {netflow_data.flows}")
            if len(netflow_data.flows) > 0:
                return netflow_data
            else:
                return None
        except v9.V9TemplateNotRecognized:
             self.__log.warning(f"Не удалось распарсить пакет от {src_ip}. Не обнаружен шаблон. Продолжаем")
             return None

    async def stop(self):
        self.__log.info("Останавливаем сервер.")
        self.__is_running = False
        if self.__soc != None:
            self.__soc.close
            self.__soc = None
        else:
            pass

    def get_dataset_buffer(self):
        """
        Метод возвращает буфер датасетов без очистки буфера. (А нужен ли такой метод?)
        """
        return self.__dataset_buffer

    def clear_dataset_buffer(self):
        """
        Метод очищает буфер датасетов
        """
        self.__dataset_buffer = []

    def pop_dataset_buffer(self):
        """
        Метод возвращает буфер датасетов и очищает его.
        """
        ds_buffer = self.__dataset_buffer
        self.__dataset_buffer = []
        return ds_buffer

