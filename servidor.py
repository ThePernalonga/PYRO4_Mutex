# Trabalho 2 de Sistemas Distribuidos
# Arquitetura Cliente-Servidor, Eventos e Notificações,
#
# JAVA RMI ou PYRO
#
# Andre L. G. Santos 2090279

# Pyro4 - comunicacao entre objetos de um cliente e servidor

import Pyro4
import uuid
import sys
import Crypto.Hash.SHA256
import Crypto.PublicKey.RSA
import Crypto.Random


TOKEN = ["Coca-cola", "Pepsi"]
SIGN_PUB = []
SIGN_PRI = []

REC1_FREE = True
REC2_FREE = True

PROC_NAME_LIST = []

class servidor(object):
  
  filaRec1 = []
  filaRec2 = []
  
  @Pyro4.expose
  def msgIni(self, name):
    print("Sua conexão foi estabelecida com sucesso! ID: " + name)
    PROC_NAME_LIST.append(name)
    return 1
    
  def get_recurso(self, tipo):
    if tipo == "Coca":
      if REC1_FREE == True:
        REC1_FREE = False
        return 1
      else:
        filaRec1.append(PROC_NAME_LIST[-1])
      
    
  @Pyro4.expose
  def AcessoRecurso(self, name, tipo):
    if tipo == "Coca":
      return print("\ncoca")
    elif tipo == "Pepsi":
      return print("\npepsi")
  
  def chavesPP():
    print("Gerando chaves...")
    SIGN_PUB = Crypto.PublicKey.RSA.generate(1024)
    SIGN_PRI = SIGN_PUB.exportKey()
    SIGN_PUB = SIGN_PUB.publickey().exportKey()
    return 1
  
  @Pyro4.expose
  def get_public_key(self):
    return SIGN_PUB
  
  print("Servidor iniciado!")
  try:
    inicio = chavesPP()
    if inicio == 1:
      print("Chaves geradas com sucesso!")
    else:
      print("Erro ao gerar chaves!")
      raise RuntimeError()
      
  
  except RuntimeError as e:
      # Any other exception - something happened, exit
      print('Reading error: '.format(str(e)))
      sys.exit()
      
  
    

daemon = Pyro4.Daemon()
uri = daemon.register(servidor)
print(uri)
ns = Pyro4.locateNS()
ns.register("Servidor", uri)
daemon.requestLoop()
