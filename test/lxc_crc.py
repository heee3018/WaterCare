from binascii  import unhexlify as str2hex

def CRC(address):
    return ('%x' %sum(str2hex('73FD52' + address + 'FFFFFFFF')))[-2:]

if __name__ == "__main__":
    address = input('주소를 입력해주세요. 예) 20201316\n')
    print(CRC(address))