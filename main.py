#Здесь будем все запускать...
import asyncio
import logging
from flowreciever import NetFlowV9Listener

async def main():
    # Настроем логирование. Тут можно покрутить формат вывода данных - для этого все уже есть.
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter(('%(asctime)s - %(name)s - %(levelname)s: %(message)s'), datefmt= '%d-%m-%Y %H:%M:%S'))
    root_logger.addHandler(log_handler)
    root_logger.setLevel(logging.DEBUG)

    nf_listener = NetFlowV9Listener()
    try:
       await nf_listener.start()
       await nf_listener.listen()
    except asyncio.exceptions.CancelledError:
        root_logger.info("Все корутины отменяются...")
    except KeyboardInterrupt:
        root_logger.info("Нажата Ctrl + C. Останавливаемся!")
    finally:
        await nf_listener.stop()
        root_logger.info("Сервер остановлен.")


if __name__ == "__main__":
    #main_test("0.0.0.0", 2055)
    asyncio.run(main())

