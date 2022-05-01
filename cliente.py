# Trabalho 2 de Sistemas Distribuidos
# Arquitetura Cliente-Servidor, Eventos e Notificações,
#
# JAVA RMI ou PYRO
#
# Andre L. G. Santos 2090279

# Pyro4 - comunicacao entre objetos de um cliente e servidor
# uuid - gerador de identificadores univocos

import Pyro4
import uuid

OBJ = "Servidor" # Nome do objeto que deseja conectar

  
URI = Pyro4.locateNS().lookup(OBJ)

SIGN_PUB = ""
TOKEN = [] # Vazio por enquanto
PROCID = str(uuid.uuid1())[:8]

ini = Pyro4.core.Proxy(URI)
connec = ini.msgIni(PROCID)

class Cliente(object):
  
  print("Bem vindo ao sistema!\nVoce está conectado agora com " + OBJ)

  while True:
    if connec != 1:
      print("Erro ao conectar com o servidor!")
      break
    
    resp = input("\n1 - Solicitar acesso ao recurso\n2 - Ver se há chave publica\n3 - Sair\n\n")
    
    if resp == "1":
      alter = input("\n Qual você deseja solicitar?\n 1 - Coca-Cola\n 2 - Pepsi\n")
      
      while True:
        if alter == "1":
          if SIGN_PUB != "":
            SIGN_PUB = ini.get_public_key()
          ini.AcessoRecurso(PROCID, "Coca")
          alter = 0
          break
          
        elif alter == "2":
          if SIGN_PUB != "":
            SIGN_PUB = ini.get_public_key()
          ini.AcessoRecurso(PROCID, "Pepsi")
          alter = 0
          break
          
        else:
          print("\nOpção inválida!\n")
        
          
      
    elif resp == "2":
      if SIGN_PUB != []:
        print(SIGN_PUB)
      else:
        print("Não há chave ainda!")
    elif resp == "3":
      break
    else:
      print("Comando inválido!")
      