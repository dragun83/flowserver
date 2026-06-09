## Простая (я надеюсь) сборка для контроля трафика netflow с визуализацией через grafana

Надеюсь удастся обойтись без кода. Стандартными средствами. Но есть предчувствие, что нет.

### Инициализация БД

# Зайти в контейнер ClickHouse
```
docker exec -it clickhouse clickhouse-client
```
# Создать таблицу
```
CREATE TABLE IF NOT EXISTS netflow (
    stamp_inserted DateTime DEFAULT now(),
    stamp_updated DateTime,
    src_ip IPv4,
    dst_ip IPv4,
    src_port UInt16,
    dst_port UInt16,
    proto UInt8,
    bytes UInt64,
    packets UInt64,
    src_as UInt32,
    dst_as UInt32,
    flows UInt32
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(stamp_inserted)
ORDER BY (stamp_inserted, src_ip, dst_ip)
TTL stamp_inserted + INTERVAL 90 DAY;
```
# Проверка (должно вернуть 0)
```
SELECT count() FROM netflow;
```