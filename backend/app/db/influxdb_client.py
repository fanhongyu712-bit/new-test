from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from ..core.config import settings


class InfluxDBManager:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        if self._client is None:
            self._client = InfluxDBClient(
                url=settings.INFLUXDB_URL,
                token=settings.INFLUXDB_TOKEN,
                org=settings.INFLUXDB_ORG,
            )
    
    def disconnect(self):
        if self._client:
            self._client.close()
            self._client = None
    
    @property
    def client(self) -> InfluxDBClient:
        if self._client is None:
            raise RuntimeError("InfluxDB client not connected")
        return self._client
    
    def get_write_api(self):
        return self.client.write_api(write_options=SYNCHRONOUS)
    
    def get_query_api(self):
        return self.client.query_api()


influxdb_manager = InfluxDBManager()
