Mode    = 'master'
Address = [
    # '20201307', 
    # '20201312',
    # '20201314',
    # '20201315',
    # '20201316',
    # '20201317',
    '21060001',
    '21060002',
    '21060003',
    '21060004',
    '21060005',
    '21060006',
    '21060007',
    '21060008',
    '21060009',
    '21060010'
]

# Initial setting
save_as_csv        = True
send_to_db         = False
detected_addresses = list()
serial_info        = {'baudrate': 2400,
                      'bytesize': 8,
                      'stopbits': 1,
                      'parity': 'E',
                      'timeout': 1}