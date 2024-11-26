import serial
import time
from threading import Thread
from icecream import ic

class Sensor:
    def __init__(self,ser_id:str,callback) -> None:

        self.ser = serial.Serial(
            port=ser_id, # 根据实际情况修改串口号
            baudrate=115200,  # 与Arduino代码中相同的波特率
            timeout=1,  # 读取超时时间1秒
        )
        self.callback = callback
        assert self.ser.is_open,"串口未打开"
        self._thread = Thread(target=self.handle,daemon=True)
        self._thread.start()
        

    def parse_pressure_data(self,data: bytes) -> list[int]:
        # 检查数据长度
        if len(data) != 35:
            raise ValueError("Data length must be 35 bytes")
        
        # 计算校验和（前34位之和的低8位）
        checksum = sum(data[:34]) & 0xFF
        
        # 检查校验和是否匹配
        if checksum != data[34]:
            raise ValueError(f"Checksum mismatch: calculated {checksum}, received {data[34]}")
        
        # 解析数据
        result = []
        for i in range(2, 34, 2):
            value = (data[i] << 8) | data[i + 1]
            result.append(value)
        
        return result
    
    def handle(self):
        while True:
            if not self.ser.in_waiting:
                time.sleep(0.05)
                continue

            data = self.ser.read(35)

            if data[:2] != b"\xaa\x01":  # 运气不好，读到的数据不是帧头
                if self.ser.read() == b"\xaa" and self.ser.read() == b"\x01":
                    data = b"\xaa\x01" + self.ser.read(33)
            
            try:
                parsed_data = self.parse_pressure_data(data)
                self.callback(parsed_data)
            except ValueError:
                continue
