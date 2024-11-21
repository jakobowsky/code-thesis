import time

def calculate_time(func):
    def inner_f(*args, **kwargs):
        begin = time.time()
        
        data = func(*args, **kwargs)

        end = time.time()
        data["time"] = end - begin
        return data

    return inner_f