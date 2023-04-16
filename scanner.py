#!/usr/bin/python3
import sys 
import socket
from datetime import datetime

if len(sys.argv)==2 :
    target= socket.gethostbyname(sys.argv[1])
else: 
    print("Yanlış bir parametre girdiniz")
    print("kullanım : python3 scanner.py <ip adress>")
    sys.exit()

print("=" * 50)
print("Tarama Yapılıyor")
print("Tarama başlatıldı :"+str(datetime.now()))
print("=" * 50)

try :
    for port in range(1,23): #Numaraları arasındaki portları tarar
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        result = s.connect_ex((target,port))
        #print("Port Taranıyor...{}".format(port))
        if result == 0 :
            açık_portlar=print("{} Numaralı port açık".format(port)) 
        s.close()
    print(açık_portlar)
except KeyboardInterrupt :
    print('\n')
    print("="*50)
    print("\nProgramdan Çıkılıyor...")
    print("="*50)
    sys.exit()

except socket.gaierror : 
    print("Adres Çözümlenemedi")
    sys.exit()

except socket.error :
    print("Bağlantı Başarısız!!")
    sys.exit()
