# Trabalho 2 de Sistemas Distribuidos
# Arquitetura Cliente-Servidor, Eventos e Notificações,
#
# JAVA RMI ou PYRO
#
# Andre L. G. Santos 2090279

import uuid
import sys
import Pyro4
import base64
from Crypto.Hash import SHA256
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from ast import Bytes
from threading import Thread

OBJ = "Servidor" # Nome do objeto que deseja conectar

# Critoreios para Conexao com o Servidor
URI = Pyro4.locateNS().lookup(OBJ)
refConnec = Pyro4.core.Proxy(URI)


SIGN_PUB = "" # Assinatura publica do servidor
PROCID = str(uuid.uuid1())[:8] # Identificador do processo
connec = refConnec.msgIni(PROCID) # Inicializa o processo

VERI = PKCS115_SigScheme # Verificador de assinatura

# Identificacao de recurso
COCA = 1
PEPSI = 2

# Classe de callback
class CallbackHandler(object):
  @Pyro4.expose
  @Pyro4.callback
  def call1(self):
    print("Callback recebido do servidor!")
    
  @Pyro4.expose
  @Pyro4.callback
  def notify(self, signature, hash, msg):
    print(type(hash))
    print(hash)
    print(type(signature))
    print(signature)
    hash = base64.b64decode(hash)
    try:
      VERI.verify(hash, signature['data'])
      print(">Notificando Servidor: " + msg)
    except:
      print(">Notificacao Falsa!")
  
  def loopThread(daemon):
    daemon.requestLoop()
    
    
# Registra callbacks no servico de nomes
daemon = Pyro4.core.Daemon()
callback = CallbackHandler()
daemon.register(callback)

# Classe principal
class Cliente(object):
  
  print("Bem vindo ao sistema!\nVoce está conectado agora com " + OBJ)
  
  # Inicializa a thread de callbacks
  msg = Thread(target=CallbackHandler.loopThread, args=(daemon, ))
  msg.setDaemon(True)
  msg.start()
  # Realiza o test do primeiro callback
  refConnec.doCallback(callback)


# Loop principal, checa se foi feita mesmo a conexão
  while True:
    # caso aconteca algum erro de conexão ele fecha o programa
    if connec != 1:
      print("Erro ao conectar com o servidor!")
      sys.exit()
    
    resp = input("\n1 - Solicitar acesso ao recurso\n2 - Ver se há chave publica\n3 - Liberar o Recurso\n4 - Sair\n\n")
    
    if resp == '1':
      
      while True:
        alter = input("\nQual você deseja solicitar?\n1 - Coca-Cola\n2 - Pepsi\n")
        if alter == '1':
          if SIGN_PUB != "": # Checa se ja possui chave publica
            # global VERI
            SIGN_PUB = refConnec.get_public_key()
            VERI = PKCS115_SigScheme(SIGN_PUB)
          refConnec.iniCallbacks1(callback) # Coloca na fila o callback
          refConnec.AcessoRecurso(PROCID, COCA) # Solicita o recurso
          alter = 0
          break
          
        elif alter == '2':
          if SIGN_PUB != "":
            SIGN_PUB = refConnec.get_public_key()
          refConnec.iniCallbacks2(callback)
          refConnec.AcessoRecurso(PROCID, PEPSI)
          alter = 0
          break
        
        else:
          print("\nOpção inválida!")
        
    elif resp == "2":
      if SIGN_PUB != []:
        print(SIGN_PUB)
      else:
        print("Não há chave ainda!")
        
    elif resp == '3':
      if refConnec.isClientWithRec(PROCID): # Checa se o cliente esta com o recurso
        while True:
          alter = input("\nQual você deseja liberar?\n1 - Coca-Cola\n2 - Pepsi\n")
          if alter == '1':
            print("Liberando recurso...")
            refConnec.freeRec(COCA)
            break
          elif alter == '2':
            print("Liberando recurso...")
            refConnec.freeRec(PEPSI)
            break
          else:
            print("\nOpção inválida!\n")

      else:
        print("Não é possível liberar o recurso, pois não é o dono!")
        
    elif resp == "4":
      refConnec.removeClient(PROCID)
      sys.exit()
    else:
      print("Comando inválido!")


