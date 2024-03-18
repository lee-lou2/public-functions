import psutil

# 시스템의 메모리 사용 상태를 가져옵니다.
memory_usage = psutil.virtual_memory()

# 전체 메모리와 사용 중인 메모리를 계산합니다.
total_memory = memory_usage.total
used_memory = memory_usage.used
free_memory = memory_usage.free

# 전체 메모리 대비 사용 중인 메모리의 비율을 백분율로 계산합니다.
memory_usage_percent = memory_usage.percent

# 기가 바이트로 표시
print(f"memory_usage: {memory_usage}")
print(f"Total memory is: {total_memory / 1024 / 1024 / 1024} GB")
print(f"Used memory is: {used_memory / 1024 / 1024 / 1024} GB")
print(f"Free memory is: {free_memory / 1024 / 1024 / 1024} GB")
print(f"Current memory usage is: {memory_usage_percent}%")
print(int(memory_usage_percent))

# 메모리 사용률이 80%를 넘는지 확인합니다.
if memory_usage_percent > 80:
    print("Memory usage is over 80%!")
else:
    print("Memory usage is under 80%.")
