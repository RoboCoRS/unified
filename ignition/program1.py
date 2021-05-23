from time import sleep
if __name__ == "__main__":
    try:
        i = 0
        while True:
            print(f'{i}           ', end='\r')
            i += 1
            sleep(1)
    except KeyboardInterrupt:
        pass
