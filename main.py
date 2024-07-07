from FlightRadar.Interface import Interface
from FlightRadar.DataBase import telechargementBaseDonnee

# Appel des fonctions pour télécharger les bases de données fournies par la FAA et l'EASA
telechargementBaseDonnee.base_de_donnees_FAA()
telechargementBaseDonnee.base_de_donnees_EASA()

# On crée l'objet Interface
interface = Interface.Interface()


# on lance l'interface
interface.mainloop()
