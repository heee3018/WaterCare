import os
import pandas as pd

def toCSV(item, path, file_name, save_data):    
    if item == 'lxc':
        df = pd.DataFrame([save_data], columns=['datetime', 'address', 'flow_rate', 'total_volume'])
        
        if not os.path.exists(path + file_name):
            df.to_csv(path + file_name, index=False, mode='w', encoding='utf-8-sig')
            
        else:
            df.to_csv(path + file_name, index=False, mode='a', encoding='utf-8-sig', header=False)

    elif item == 'ms5837':
        df = pd.DataFrame([save_data], columns=['datetime', 'pressure_bar', 'temperature'])
        
        if not os.path.exists(path + file_name):
            df.to_csv(path + file_name, index=False, mode='w', encoding='utf-8-sig')
            
        else:
            df.to_csv(path + file_name, index=False, mode='a', encoding='utf-8-sig', header=False)
