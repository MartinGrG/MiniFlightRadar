"""Fichier à lancer pour démarrer l'application"""

from FlightRadar.Interface import Interface
from FlightRadar.DataBase import telechargementBaseDonnee

# Appel des fonctions pour télécharger les bases de données fournies par la FAA et l'EASA
telechargementBaseDonnee.base_de_donnees_faa()
telechargementBaseDonnee.base_de_donnees_easa()

# On crée l'objet Interface
interface = Interface.Interface()

# on lance l'interface
interface.mainloop()
