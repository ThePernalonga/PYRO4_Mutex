# Trabalho 2 de Sistemas Distribuidos
# Arquitetura Cliente-Servidor, Eventos e Notificações,
#
# JAVA RMI ou PYRO
#
# Andre L. G. Santos 2090279

# Pyro4 - comunicacao entre objetos de um cliente e servidor
# uuid - gerador de identificadores univocos

from threading import Thread
import Pyro4
import uuid

OBJ = "Servidor" # Nome do objeto que deseja conectar
  
URI = Pyro4.locateNS().lookup(OBJ)
refConnec = Pyro4.core.Proxy(URI)

SIGN_PUB = ""
TOKEN = [] # Vazio por enquanto
PROCID = str(uuid.uuid1())[:8]
connec = refConnec.msgIni(PROCID)

COCA = 1
PEPSI = 2

class CallbackHandler(object):
  @Pyro4.expose
  @Pyro4.callback
  def call1(self):
    print("Callback recebido do servidor!")
  
  def loopThread(daemon):
    daemon.requestLoop()
    
    

daemon = Pyro4.core.Daemon()
callback = CallbackHandler()
daemon.register(callback)


class Cliente(object):
  
  print("Bem vindo ao sistema!\nVoce está conectado agora com " + OBJ)
  
  # print(refConnec.doCallback(callback, "test"))
  msg = Thread(target=CallbackHandler.loopThread, args=(daemon, ))
  msg.setDaemon(True)
  msg.start()


# Loop principal, checa se foi feita mesmo a conexão
  while True:
    refConnec.doCallback(callback)
    if connec != 1:
      print("Erro ao conectar com o servidor!")
      break
    
    resp = input("\n1 - Solicitar acesso ao recurso\n2 - Ver se há chave publica\n3 - Liberar o Recurso\n4 - Sair\n\n")
    
    if resp == '1':
      
      while True:
        alter = input("\nQual você deseja solicitar?\n1 - Coca-Cola\n2 - Pepsi\n")
        if alter == '1':
          if SIGN_PUB != "":
            SIGN_PUB = refConnec.get_public_key()
          print(refConnec.AcessoRecurso(PROCID, COCA))
          alter = 0
          break
          
        elif alter == '2':
          if SIGN_PUB != "":
            SIGN_PUB = refConnec.get_public_key()
          print(refConnec.AcessoRecurso(PROCID, PEPSI))
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
      if refConnec.isClientWithRec(PROCID):
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
      break
    else:
      print("Comando inválido!")


