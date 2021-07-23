import os
import pandas as pd

def lxc_to_csv(path, data):
    df = pd.DataFrame([data], columns=['datetime', 'address', 'flow_rate', 'total_volume'])

    if not os.path.exists(path):
        df.to_csv(path, index=False, mode='w', encoding='utf-8-sig')
        
    else:
        df.to_csv(path, index=False, mode='a', encoding='utf-8-sig', header=False)
