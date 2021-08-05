from library   import flip, to_select_command
from binascii  import hexlify as hex2str

if __name__ == '__main__':
    address = input('Type the address : ')
    print(hex2str(to_select_command(flip(address))))