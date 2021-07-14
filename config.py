Mode = 'master'
Address = ['20201307', 
           '20201312',
           '20201314',
           '20201315',
           '20201316',
           '20201317']

detected_addresses = list()

save_as_csv = False
send_to_db  = False

serial_info = {
    'baudrate': 2400,
    'bytesize': 8,
    'stopbits': 1,
    'parity': 'E',
    'timeout': 3
}
