from time import sleep
from subprocess import getoutput


for i in range(60):
    
    sleep(1)
    ip = getoutput('hostname -I')
    
    if len(ip) > 5 :
        print("ip: " + ip)
        input("Done")
        exit()
    
    else:
        continue
input('Error')
exit()
오류 : 다음 파일에 대한 로컬 변경 사항은 병합으로 덮어 씁니다.
Autorun_IP_Verification.py

aborting병합하기 전에 변경 사항을 커밋하거나 숨기십시오.