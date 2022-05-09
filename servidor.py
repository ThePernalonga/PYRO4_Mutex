# Trabalho 2 de Sistemas Distribuidos
# Arquitetura Cliente-Servidor, Eventos e Notificações,
#
# JAVA RMI ou PYRO
#
# Andre L. G. Santos 2090279

# Pyro4 - comunicacao entre objetos de um cliente e servidor

import sys

import Pyro4
import Crypto.Hash.SHA256
import Crypto.PublicKey.RSA
import Crypto.Random
from threading import Thread, Lock, Event

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

@Pyro4.behavior(instance_mode="single")
class Servidor(object):
  @Pyro4.expose  
  def doCallback(self, callback):
    print(">Realizando callback no client")
    return callback.call1()
    
  
  lock1 = Lock()
  lock2 = Lock()
  exit1 = Event()
  exit2 = Event()
  
  @Pyro4.expose
  def isClientWithRec(self, procid):
    self.doCallback(self.callback, "test")
    return procid == IDENTIFIER1
  
  @Pyro4.expose
  def freeRec(self, rec):
    if rec == COCA:
      self.exit1.set()
    elif rec == PEPSI:
      self.exit2.set()
    else:
      return -1
  
  def task1(self, lock, identifier, value):
    global REC1_FREE, IDENTIFIER1
    with lock:
      REC1_FREE = False
      # print(FILAREC1)
      if len(FILAREC1) == 0:
        IDENTIFIER1 = ""
        REC1_FREE = True
        # print(REC1_FREE)
        print(f'>Processo {identifier} liberou! COCA')
      else:
        self.exit1.clear()
        IDENTIFIER1 = FILAREC1[0]
        print(f'>Processo {identifier} está segurando por {value} segundos')
        while not self.exit1.is_set():
          self.exit1.wait(value)
          self.exit1.set()
        FILAREC1.pop(0)
        REC1_FREE = True
        self.lock1 = Lock()
        self.task1(self.lock1, IDENTIFIER1, value)
  
  def task2(self, lock, identifier, value):
    global REC2_FREE, IDENTIFIER2
    with lock:
      REC2_FREE = False
      # print(FILAREC2)
      if len(FILAREC2) == 0:
        IDENTIFIER2 = ""
        REC2_FREE = True
        # print(REC2_FREE)
        print(f'>Processo {identifier} liberou! PEPSI')
      else:
        self.exit2.clear()
        IDENTIFIER2 = FILAREC2[0]
        print(f'>Processo {identifier} está segurando por {value} segundos')
        while not self.exit2.is_set():
          self.exit2.wait(value)
          self.exit2.set()
        FILAREC2.pop(0)
        REC2_FREE = True
        self.lock2 = Lock()
        self.task2(self.lock2, IDENTIFIER2, value)
        
  @Pyro4.expose
  def msgIni(self, name):
    print("Sua conexão foi estabelecida com sucesso! ID: " + name)
    PROC_NAME_LIST.append(name)
    return 1

  @Pyro4.expose
  def removeClient(self, name):
    print("Cliente " + name + " foi desconectado!")
    PROC_NAME_LIST.remove(name)
    return 1

  @Pyro4.expose
  def AcessoRecurso(self, name, tipo: int):
    global REC1_FREE, REC2_FREE
    if tipo == COCA:
      global FILAREC1
      if REC1_FREE == True:
        # print(REC1_FREE)
        FILAREC1.append(name)
        Thread(target = self.task1, args=(self.lock1, name, TEMP_MAX)).start()
      
      elif REC1_FREE == False:
        FILAREC1.append(name)
        return "Recurso não disponível, entrando na fila..."
      
      return f"Recurso {tipo} alocado para {name}"
    
    if tipo == PEPSI:
      global FILAREC2
      if REC2_FREE == True:
        # print(REC2_FREE)
        FILAREC2.append(name)
        Thread(target = self.task2, args=(self.lock2, name, TEMP_MAX)).start()
      
      elif REC2_FREE == False:
        FILAREC2.append(name)
        return "Recurso não disponível, entrando na fila..."
      
      return f"Recurso {tipo} alocado para {name}"

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
