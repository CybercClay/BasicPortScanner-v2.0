#!/usr/bin/python3

import socket
import sys
import time

print("""
    ____             __     _____                                 
   / __ \____  _____/ /_   / ___/_________ _____  ____  ___  _____
  / /_/ / __ \/ ___/ __/   \__ \/ ___/ __ `/ __ \/ __ \/ _ \/ ___/
 / ____/ /_/ / /  / /_    ___/ / /__/ /_/ / / / / / / /  __/ /    
/_/    \____/_/   \__/   /____/\___/\__,_/_/ /_/_/ /_/\___/_/     
                                                                 
                                                                  

------------------- Made by CyberClay -----------------------------        


                                                          
""")
print("Özel bir port aralığı girmek için; [1]")
print("İlk 1000 portu taramak için; [2]")
print("\n")
try:
	tarama_türü = int(input("Tarama türünü giriniz: "))
	if tarama_türü == 1:
		def tarama(ip, baslangıc_port, bitis_port):
			for port in range(baslangıc_port, bitis_port + 1):
				soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				soket.settimeout(1)

				if soket.connect_ex((ip, port)) == 0:
					print(f"{port} Numaralı port açık. ")
			
				soket.close()
	
		ip = input("İp adresi giriniz: ")
		baslangıc_port = int(input("Başlangıç portunun numarasını girin (minimum 1)"))
		bitis_port = int(input("Bitiş portunun numarasını girin (en fazla 65535)"))
		print("Taranıyor")
		tarama(ip, baslangıc_port, bitis_port)
 	
	if tarama_türü == 2: 			
		def tarama2(ip):
			for port in range(1, 1001):
				soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				soket.settimeout(1)
			
				if soket.connect_ex((ip, port)) == 0:
					print(f"{port} Numaralı port açık. ")
				soket.close()
		ip = input("İp adresi giriniz: ")
		tarama2(ip)

except KeyboardInterrupt :
    print("\nProgramdan Çıkılıyor...")
    sys.exit()

except socket.gaierror : 
    print("Adres Çözümlenemedi, ip adresini düzgün girdiğinizden emin olunuz.")
    sys.exit()

except socket.error :
    print("Bağlantı Başarısız!!")
    sys.exit()


    

