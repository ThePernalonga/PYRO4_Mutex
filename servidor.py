# Trabalho 2 de Sistemas Distribuidos
# Arquitetura Cliente-Servidor, Eventos e Notificações,
#
# JAVA RMI ou PYRO
#
# Andre L. G. Santos 2090279

# Pyro4 - comunicacao entre objetos de um cliente e servidor

from logging.config import IDENTIFIER
import sys

import Pyro4
import Crypto.Hash.SHA256
import Crypto.PublicKey.RSA
import Crypto.Random
from time import sleep
from threading import Thread
from threading import Lock
from threading import Event


TOKEN = ["Coca-cola", "Pepsi"]
SIGN_PUB = []
SIGN_PRI = []

TEMP_MAX = 10

COCA = 1
PEPSI = 2

IDENTIFIER1 = ""
IDENTIFIER2 = ""
REC1_FREE = True
REC2_FREE = True

FILAREC1 = []
FILAREC2 = []

PROC_NAME_LIST = []

class Servidor(object):
  
  lock = Lock()
  exit = Event()
  
  @Pyro4.expose
  def isClientWithRec(self, procid):
    return procid == IDENTIFIER1
  
  @Pyro4.expose
  def freeRec(self, rec):
    if rec == COCA:
      self.exit.set()
    # elif rec == PEPSI:
    #   self.lock.release()
    else:
      return -1
  
  def task(self, lock, identifier, value):
    global REC1_FREE, IDENTIFIER1
    with lock:
      REC1_FREE = False
      print(FILAREC1)
      # IDENTIFIER = identifier
      if len(FILAREC1) == 0:
        IDENTIFIER1 = ""
        REC1_FREE = True
        print(REC1_FREE)
        print(f'>Processo {identifier} está livre!\n')
      else:
        self.exit.clear()
        IDENTIFIER1 = FILAREC1[0]
        print(f'>Processo {identifier} está em uso durante {value} segundos')
        while not self.exit.is_set():
          self.exit.wait(value)
          self.exit.set()
        FILAREC1.pop(0)
        REC1_FREE = True
        self.lock = Lock()
        self.task(self.lock, IDENTIFIER1, value)
        

  
  @Pyro4.expose
  def msgIni(self, name):
    print("Sua conexão foi estabelecida com sucesso! ID: " + name)
    PROC_NAME_LIST.append(name)
    return 1

  @Pyro4.expose
  def AcessoRecurso(self, name, tipo: int):
    global REC1_FREE, REC2_FREE
    if tipo == COCA:
      global FILAREC1
      if REC1_FREE == True:
        print(REC1_FREE)
        FILAREC1.append(name)
        Thread(target = self.task, args=(self.lock, name, TEMP_MAX)).start()
      
      elif REC1_FREE == False:
        FILAREC1.append(name)
        return "not not free"
      
      return "coca " + name
    
    elif tipo == PEPSI:
      return "pepsi " + name

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
uri = daemon.register(Servidor)
print(uri)
ns = Pyro4.locateNS()
ns.register("Servidor", uri)
daemon.requestLoop()
