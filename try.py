from s826 import S826

# 创建 S826 实例
dac = S826()

# 发送简单的电流输出信号
pin_number = 1  # 你的设备的实际 PIN 号
output_value = 1.0  # 设定一个简单的输出值

dac.s826_aoPin(pin_number, output_value)
print(f"✅ 发送电流: pin {pin_number}, value {output_value}")
