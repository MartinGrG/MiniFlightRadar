""" Ce script défini la classe interface. Cet objet correspond à une fenêtre
pop up permettant à l'utilisateur d'intéragir avec le code. """

# Librairies pour l'interface
import customtkinter
from tkintermapview import TkinterMapView
import tkinter as tk
import math
from PIL import Image, ImageTk
# Librairies pour les timestamp unix
import datetime
import time
# Librairies pour la gestion des données
from DataBase import sortie, airplane_traj
import pandas as pd


customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"

class Interface(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        self.liste_vols = pd.DataFrame({})
        self.airport_depart = ''
        self.traj = []
        self.avion_image = Image.open("plane_img.png")
        self.marker_avion = None

        # configuration de la fenêtre :
        self.title("Panneau usager")  # titre
        self.geometry("1300x600")  # dimensions de la fenètre
        self.attributes('-topmost', True)  # on fait passer la fenètre au-dessus du reste à l'apparition

        # configuration de la grille de base (1x3) :
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # création des frames de l'interface :
        self.frame_gauche = customtkinter.CTkFrame(self, corner_radius=5)
        self.frame_gauche.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
        self.frame_gauche.grid_columnconfigure((1,2), weight=1)
        self.frame_gauche.grid_rowconfigure(5, weight=1)

        self.frame_milieu = customtkinter.CTkFrame(self, corner_radius=5)
        self.frame_milieu.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=(5,5), pady=10)
        self.frame_milieu.grid_columnconfigure(0, weight=1)
        self.frame_milieu.grid_rowconfigure((0, 1), weight=1)

        self.frame_droite = customtkinter.CTkFrame(self, corner_radius=5)
        self.frame_droite.grid(row=0, column=2, rowspan=3, sticky="nsew", padx=(5,10), pady=10)
        self.frame_droite.grid_columnconfigure(0,weight=1)
        self.frame_droite.grid_rowconfigure(2, weight=1)

        # Création des éléments de la frame gauche :
        self.label_airport = customtkinter.CTkLabel(self.frame_gauche, text="Code de l'aéroport de départ")
        self.label_airport.grid(row=0, column=0, columnspan=3, sticky="nsw", padx=10, pady=(5,0))

        self.input_airport = customtkinter.CTkEntry(self.frame_gauche, placeholder_text="ex : AX500")
        self.input_airport.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0,5))
        self.input_airport.bind("<KeyRelease>", self.check_text_airport)

        # prochainement remplacé par un calendrier plus facile d'utilisation
        self.label_date = customtkinter.CTkLabel(self.frame_gauche, text="Selectionnez la date")
        self.label_date.grid(row=2, column=0, sticky="nsw", padx=10, pady=(5, 0))

        self.input_date = customtkinter.CTkEntry(self.frame_gauche, placeholder_text="aaaa/mm/jj")
        self.input_date.grid(row=3, column=0, sticky="nsew", padx=(10,0), pady=(0, 5))
        self.input_date.bind("<KeyRelease>", self.check_text_date)

        self.input_heure_debut = customtkinter.CTkEntry(self.frame_gauche, placeholder_text="de : 13:00")
        self.input_heure_debut.grid(row=3, column=1, sticky="nsew", padx=5, pady=(0, 5))
        self.input_heure_debut.bind("<KeyRelease>", self.check_text_heure_debut)

        self.input_heure_fin = customtkinter.CTkEntry(self.frame_gauche, placeholder_text="à : 15:30")
        self.input_heure_fin.grid(row=3, column=2, sticky="nsew", padx=(0,10), pady=(0, 5))
        self.input_heure_fin.bind("<KeyRelease>", self.check_text_heure_fin)
        self.input_heure_fin.configure(state="disabled")

        self.button_search = customtkinter.CTkButton(self.frame_gauche, corner_radius=5, text="Rechercher", command=self.button_search_event)
        self.button_search.grid(row=4, column=0,columnspan=3, sticky="nsew", padx=10, pady=(0, 5))

        self.scroframe_liste_vols = customtkinter.CTkScrollableFrame(self.frame_gauche)
        self.scroframe_liste_vols.grid(row=5,column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.scroframe_liste_vols.grid_columnconfigure((0,1), weight=1)

        # Configuration de la frame du milieu
        # On ajoute la map
        self.map_widget = TkinterMapView(self.frame_milieu, corner_radius=10, width=700)
        self.map_widget.grid(row=0, rowspan=2, sticky="nswe", padx=10, pady=10)
        self.map_widget.set_position(48.860381, 2.338594)
        self.map_widget.set_zoom(5)

        # Ajouter un rectangle avec les infos du vol sur la mapview
        # (obtenu en fouillant dans la librairie retro-Engineering au plus bas level possible)
        position_info = (450, 460)
        width_infos = 250
        height_infos = 150
        self.canvas_rect = self.map_widget.canvas.create_polygon(position_info[0], position_info[1],
                                                                 position_info[0] + width_infos,
                                                                 position_info[1],
                                                                 position_info[0] + width_infos,
                                                                 position_info[1] + height_infos,
                                                                 position_info[0],
                                                                 position_info[1] + height_infos,
                                                                 width=10,
                                                                 fill="gray25", outline="gray25",
                                                                 tag="button")

        self.canvas_text = self.map_widget.canvas.create_text(math.floor(position_info[0]+10),
                                                              math.floor(position_info[1]+11),
                                                              anchor="nw",
                                                              fill="white",
                                                              tag="button",
                                                              font= ('Arial', 11,"bold"))

        # Ajout du curseur de selection de temps pendant le vol

        self.frame_curseur_temps = customtkinter.CTkFrame(self.frame_milieu)
        self.frame_curseur_temps.grid(row=2,sticky="nswe", padx=20,pady=10)
        self.frame_curseur_temps.grid_columnconfigure(1, weight=1)

        self.curseur_temps = customtkinter.CTkSlider(self.frame_curseur_temps,state="disabled", from_=2, to=100, height=25, command=self.curseur_temps_event)
        self.curseur_temps.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.curseur_temps.set(10)

        self.label_temps_indicateur = customtkinter.CTkLabel(self.frame_curseur_temps, text="__:__", corner_radius=5, fg_color="grey", padx="5", pady="5")
        self.label_temps_indicateur.grid(row=0, column=0, padx=(10,0))

        # configuration de la frame de droite

        self.label_carbon_titre = customtkinter.CTkLabel(self.frame_droite, text="Calculateur\nCO2", font=('Arial', 25, "bold"))
        self.label_carbon_titre.grid(row=0,column=0, padx=10, pady=10)

        self.frame_actuelle_emission = customtkinter.CTkFrame(self.frame_droite)
        self.frame_actuelle_emission.grid(row=1, sticky="nswe", padx=10, pady=10)
        self.frame_actuelle_emission.grid_columnconfigure(0, weight=1)

        self.label_carbon_resultat = customtkinter.CTkLabel(self.frame_actuelle_emission, text="émission carbone :")
        self.label_carbon_resultat.grid(row=1,column=0, padx=5, pady=5)

        self.frame_compare_emission = customtkinter.CTkFrame(self.frame_droite)
        self.frame_compare_emission.grid(row=2, sticky="nswe", padx=10, pady=(0,10))
        self.frame_compare_emission.grid_columnconfigure(0, weight=1)
        self.frame_compare_emission.grid_rowconfigure(3, weight=1)

        check_avions_compare_var = customtkinter.StringVar(value="off")
        self.check_avions_compare = customtkinter.CTkCheckBox(self.frame_compare_emission, text="B777 : 366kg", command= self.checkbox_event,
                                             variable=check_avions_compare_var, onvalue="on", offvalue="off")
        self.check_avions_compare.grid(row=0, sticky="nsw", padx=10, pady=10)

        self.button_export_data = customtkinter.CTkButton(self.frame_compare_emission, text="Exporter", command=self.export_event)
        self.button_export_data.grid(row=4, column=0, sticky="swe", padx=10, pady=10)

    def check_text_airport(self, event):
        """
        Cette procédure est liée à l'entrée texte input_airport de sorte qu'à chaque fois
        qu'une touche est lachée lors de la saisie, cette dernière est lancée. Elle met
        en place les mécanismes de sécurité permettant d'assurer une saisie du code de
        l'aéroport bien formatée : on s'assure que le code contient uniquement 4 lettres.

        :param tkinter.event event: Contient les informations sur la keyRealeased (pas utilisé ici, mais obligatoire)
        """
        lenght = len(self.input_airport.get())

        # On s'assure qu'aucun chiffre n'est entré
        if lenght >= 1:
            if self.input_airport.get()[lenght - 1].isnumeric():
                self.input_airport.delete(lenght - 1)

        # On s'assure de ne pas dépasser 4 caractères
        if lenght >= 5:
            self.input_airport.delete(lenght - 1)

    def check_text_date(self, event):
        """
        Cette procédure est liée à l'entrée texte input_date de sorte qu'à chaque fois
        qu'une touche est lachée lors de la saisie, cette dernière est lancée. Elle met
        en place les mécanismes de sécurité permettant d'assurer une saisie de la date
        suivant un formatage bien précis :

        | - On s'assure que la date contient tout juste 10 caractères.
        | - On s'assure que les / s'ajoutent automatiquement.
        | - On s'assure que la date ne contient que des chiffres.

        :param tkinter.event event: Contient les informations sur la keyRealeased.
        """
        lenght = len(self.input_date.get())

        # On ajoute automatiquement les / de la date seulement dans le sens de l'écriture
        if (lenght == 4 or lenght == 7) and event.keysym != "BackSpace":
            self.input_date.insert(lenght, '/')

        # On s'assure que les / sont bien présents là où ils devraient : sinon, on les ajoute
        if lenght == 5 or lenght == 8:
            if not self.input_date.get()[lenght - 1] == "/":
                self.input_date.insert(lenght - 1, '/')

        # On s'assure de ne pas dépasser la taille maximale de la date
        if lenght >= 11:
            self.input_date.delete(lenght - 1)

        # On vérifie que les caractères entrés sont des chiffres
        if lenght >= 1 and lenght != 5 and lenght != 8:
            if not self.input_date.get()[lenght - 1].isnumeric():
                self.input_date.delete(lenght - 1)

    def check_text_heure_debut(self, event):
        """
        Cette procédure est liée à l'entrée texte input_heure_debut de sorte qu'à chaque fois
        qu'une touche est lachée lors de la saisie, cette dernière est lancée. Elle met
        en place les mécanismes de sécurité permettant d'assurer une saisie de l'heure minimale
        du créneau de sélection des vols bien formatée :

        |- On s'assure que l'heure contient tout juste 5 caractères.
        |- On s'assure que les : s'ajoutent automatiquement.
        |- On s'assure que l'heure ne contient que des chiffres.
        |- On empêche l'entrée de l'heure de fin tant que l'entrée de l'heure de début n'est pas complète.

        :param tkinter.event event: Contient les informations sur la keyRealeased.
        """
        lenght = len(self.input_heure_debut.get())

        # On ajoute : au troisième caractère dans le sens de l'écriture
        if lenght == 2 and event.keysym != "BackSpace":
            self.input_heure_debut.insert(lenght, ':')

        # On s'assure que le troisième caractère est bien : : sinon on l'insère
        if lenght == 3:
            if not self.input_heure_debut.get()[lenght - 1] == ":":
                self.input_heure_debut.insert(lenght-1, ':')

        # On s'assure que seuls des chiffres sont inscrits
        if lenght >= 1 and lenght != 3:
            if not self.input_heure_debut.get()[lenght - 1].isnumeric():
                self.input_heure_debut.delete(lenght - 1)

        # On évite que les minutes dépassent 59
        if lenght == 4 and int(self.input_heure_debut.get()[lenght - 1]) >= 6:
            self.input_heure_debut.delete(lenght - 1)

        # On limite la taille maximale à 5 caractères
        if lenght >= 6:
            self.input_heure_debut.delete(lenght - 1)

        # Ici, pour éviter les mauvaises entrées entre les deux horaires, si on vient modifier l'heure de début,
        # l'algorithme supprime l'heure de fin et la bloque tant que l'heure de début n'est pas complète.
        if lenght < 5:
            self.input_heure_fin.delete(0, 5)
            self.input_heure_fin.configure(state="disabled")
        else:
            self.input_heure_fin.configure(state="normal")

    def check_text_heure_fin(self, event):
        """
        Cette procédure est liée à l'entrée texte input_heure_fin de sorte qu'à chaque fois
        qu'une touche est lachée lors de la saisie, cette dernière est lancée. Elle met
        en place les mécanismes de sécurité permettant d'assurer une saisie de l'heure maximale
        du créneau de sélection des vols bien formatée :

        |- On s'assure que l'heure contient tout juste 5 caractères.
        |- On s'assure que les : s'ajoutent automatiquement.
        |- On s'assure que l'heure ne contient que des chiffres.
        |- On vérifie que l'heure est bien supérieure à l'heure de début entrée précèdemment.

        :param tkinter.event event: Contient les informations sur la keyRealeased.
        """
        lenght = len(self.input_heure_fin.get())

        # Ajoute un : au troisième caractère seulement dans le sens de l'écriture
        if lenght == 2 and event.keysym != "BackSpace":
            self.input_heure_fin.insert(lenght, ':')

        # Vérifie si le troisième caractère est bien un : sinon on le met
        if lenght == 3:
            if not self.input_heure_fin.get()[lenght - 1] == ":":
                self.input_heure_fin.insert(lenght-1, ':')

        # On s'assure que seuls les chiffres peuvent être entrés
        if lenght >= 1 and lenght != 3:
            if not self.input_heure_fin.get()[lenght - 1].isnumeric():
                self.input_heure_fin.delete(lenght - 1)

        # On s'assure de ne pas dépasser la taille maximale de 5 caractères
        if lenght >= 6:
            self.input_heure_fin.delete(lenght - 1)

        # On s'assure que l'utilisateur ne puisse pas dépasser 60 minutes
        if lenght == 4 and int(self.input_heure_fin.get()[lenght - 1]) >= 6:
            self.input_heure_fin.delete(lenght - 1)

        # On s'assure que l'heure de fin est bien plus grande de 30min par rapport à l'heure de debut du créneau
        if lenght == 5:
            heure_fin = int(self.input_heure_fin.get()[:2]) + int(self.input_heure_fin.get()[3:5])/100
            heure_debut = int(self.input_heure_debut.get()[:2]) + int(self.input_heure_debut.get()[3:5])/100
            if heure_fin <= heure_debut+0.30:
                self.input_heure_fin.delete(0, 5)

    def button_vol_event(self, index):
        """
        Cette procédure est liée à tous les bouttons portant les informations de chaque vol dans la liste
        de la frame de gauche. Lorsqu'un des bouttons est pressé, la procédure se lance, récupère les informations
        de trajectoire du vol en question via la méthode airplane_traj(), trace cette dernière sur la mapView,
        ajoute un marqueur en forme d'avion, indique en bas à droite les informations détaillées du vol à
        l'utilisateur et envoie les données du vol au calculateur d'émission CO2.

        :param int index: Indice lié au boutton pressé (vol selectionné)
        """
        # Récupération des données de trajectoire et formatage
        self.traj = airplane_traj(index-1)
        traj = [x[1:3] for x in self.traj]

        # Affichage du marqueur sous la forme d'un avion
        if self.marker_avion is not None:
            self.marker_avion.delete()
        rotated_pil_img = self.avion_image.rotate(self.traj[0][4])
        tk_icon = ImageTk.PhotoImage(rotated_pil_img)
        self.marker_avion = self.map_widget.set_marker(traj[-1][0], traj[-1][1], icon=tk_icon)
        self.marker_avion.change_icon(tk_icon)

        # Affichage de la trajectoire du vol sur la map
        self.map_widget.delete_all_path()
        self.map_widget.set_position(traj[0][0], traj[0][1])
        self.map_widget.set_path(traj, color="#242424", width=3)

        # Adaptation du curseur au vol selectionné
        self.curseur_temps.configure(state="normal")
        self.curseur_temps.configure(to=len(self.traj))

        # Mise à jour de l'encadré montrant les informations du vol
        self.map_widget.canvas.itemconfig(self.canvas_text,
                                          text=f"Compagnie : {self.liste_vols["compagnie"].values[index-1]}\n"
                                               f"Aéroport de départ : {self.liste_vols["estDepartureAirport"].values[index-1]}\n"
                                               f"Aéroport d'arrivée : {self.liste_vols["estArrivalAirport"].values[index-1]}\n"
                                               f"Call sign : {self.liste_vols["callsign"].values[index-1]}\n"
                                               f"Numéro ICAO24 : {self.liste_vols["icao24"].values[index-1]}\n"
                                               f"Heure de départ : {timestamp_to_hour(self.liste_vols["firstSeen"].values[index-1])}\n"
                                               f"Heure d'arrivée : {timestamp_to_hour(self.liste_vols["lastSeen"].values[index-1])}\n")

        # Envoie des données de vol au calculateur CO2
        self.calculer_carbon(self.liste_vols["modelReduit"].values[index-1], calcule_distance(traj[0],traj[-1]))

    def button_search_event(self):
        """
        Cette procédure est liée au bouton button_search. Lorsque ce dernier est pressé, la procédure entre
        premièrement dans une phase de vérification afin de s'assurer que tous les champs d'entrées soient
        bien remplis. Ensuite, la procèdure formate les entrées et récupère à l'aide de la méthode sortie()
        les vols correspondant aux critères spécifiés pour les afficher dans la zone à gauche dédiée.

        """
        # Vérification de tous les champs d'entrées correctement renseignés
        etat = (len(self.input_heure_fin.get()) == 5 and len(self.input_heure_debut.get()) == 5 and
                len(self.input_airport.get()) == 4 and len(self.input_date.get()) == 10)

        # Si tout est bon, formatage et envoi des critères pour récupérer les vols correspondant
        if etat:
            airport = self.input_airport.get().upper()
            date_debut = self.input_date.get() + " " + self.input_heure_debut.get()
            date_fin = self.input_date.get() + " " + self.input_heure_fin.get()
            timestamp_debut = int(time.mktime(datetime.datetime.strptime(date_debut, "%Y/%m/%d %H:%M").timetuple()))
            timestamp_fin = int(time.mktime(datetime.datetime.strptime(date_fin, "%Y/%m/%d %H:%M").timetuple()))
            self.liste_vols = sortie(airport, timestamp_debut, timestamp_fin)

            # Clear de la zone où sera affichée la liste des avions
            for widget in self.scroframe_liste_vols.winfo_children():
                widget.destroy()
            # Affichage de chaque vol dans la zone dédiée
            i = 0
            for vol in self.liste_vols.itertuples():
                button = customtkinter.CTkButton(self.scroframe_liste_vols, corner_radius=5,
                                                 text=f"{vol.compagnie} : {vol.estDepartureAirport}-"
                                                      f"{vol.estArrivalAirport} : {timestamp_to_hour(vol.firstSeen)}-"
                                                      f"{timestamp_to_hour(vol.lastSeen)}",
                                                 command=lambda index=vol.index: self.button_vol_event(index))
                button.grid(row=i, column=0, columnspan=2, sticky="nsew", pady=1)
                i += 1

        # Cas où les critères ne sont pas complètement entrés
        else:
            print("Attention remplissez tous les champs")

    def curseur_temps_event(self, value):
        """
        Cette procédure est liée au curseur curseur_temps. A chaque déplacement, la procédure se lance afin d'afficher
        dynamiquement la trajectoire sur la mapView. De plus un marqueur sous la forme d'un avion est tracé se déplace
        et s'oriente dynamiquement. La procédure permet également d'afficher l'heure correspondante la trajectoire
        tracée.

        :param int value: Valeur renvoyée par le curseur (de 1 au nombre d'éléments composant la trajectoire moins 1).
        """
        value = int(value)
        traj = [x[1:3] for x in self.traj]
        # Affichage de l'heure dans l'espace correspondant
        self.label_temps_indicateur.configure(text=timestamp_to_hour(self.traj[value-1][0]))

        # Rotation du marqueur et déplacement de ce-dernier
        rotated_pil_img = self.avion_image.rotate(-self.traj[value-1][4])
        tk_icon = ImageTk.PhotoImage(rotated_pil_img)
        self.marker_avion.change_icon(tk_icon)
        self.marker_avion.set_position(traj[value-1][0],traj[value-1][1])

        # Mise à jour du tracé de la trajectoire
        self.map_widget.delete_all_path()
        self.map_widget.set_path(traj[0:value], color="#242424", width=3)

    def checkbox_event(self):
        print("B777")

    def export_event(self):
        print("export")

    def calculer_carbon(self, modele, distance):
        """
        Cette procédure est déclenchée à l'exécution de :func:button_vol_event et permet de récupérer l'émission
        carbone d'un modèle d'avion donné pour la distance parcourue et l'affiche dans la zone dédiée.

        :param str modele: Nom du modèle d'avion (ex : B777)
        :param float distance: Valeur de la distance parcourue calculée à l'aide de la fonction :func:calcule_distance.
        """
        print(modele)
        print(distance)
        self.label_carbon_resultat.configure(text=f"modèle : {modele}\ndistance totale : {distance}")


def timestamp_to_hour(timestamp):
    """
    Cette fonction permet de convertir un timestamp unix en heures:minutes.

    :param int timestamp: Valeur du timestamp à convertir
    :returns: String représentant la valeur de l'horodatage correspondant au timestamp d'origine
    :rtype: str
    """
    return str(datetime.datetime.fromtimestamp(timestamp))[11:16]


def date_to_timestamp(date): # En construction
    return


def calcule_distance(coord1, coord2): # En cours d'amélioration
    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]
    deltalat = lat2-lat1
    deltalon = lon2-lon1

    d = 2*6371000*math.asin(math.sqrt(math.sin(deltalat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(deltalon/2)**2))
    return d


