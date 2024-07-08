""" Ce script défini la classe interface. Cet objet correspond à une fenêtre
pop up permettant à l'utilisateur d'intéragir avec le code. """

# Librairies pour l'interface
import customtkinter
from tkintermapview import TkinterMapView
import math
from PIL import Image, ImageTk, ImageGrab
# Librairies pour les timestamp unix
import datetime
import time
# Librairies pour la gestion des données
from FlightRadar.DataBase.DataBase import sortie, airplane_traj, similar_engines, similar_models
import pandas as pd
# Librairie pour générer document PDF
from FlightRadar.PDFgenerator.Pdf_generateur import Pdf
import numpy as np
# Librairies pour emissions
from FlightRadar.CO2calculator.CarbonEmissions import passenger_carbon_emissions

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"


class Interface(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        self.liste_vols = pd.DataFrame({})
        self.airport_depart = ''
        self.traj = []
        self.avion_image = Image.open("FlightRadar/Interface/plane_img.png")
        self.marker_avion = None
        self.liste_moteurs_sim = []
        self.index_vol = None
        self.liste_emissions = [[], [[]], [[]]]
        self.liste_modele_sim = []
        # configuration de la fenêtre :
        self.title("Panneau usager")  # titre
        self.geometry("1300x600")  # dimensions de la fenètre

        # configuration de la grille de base (1x3) :
        self.grid_columnconfigure((0, 2), weight=1)
        self.grid_columnconfigure((1, 2), weight=0)

        self.grid_rowconfigure(0, weight=1)

        # création des frames de l'interface :
        self.frame_gauche = customtkinter.CTkFrame(self, corner_radius=5)
        self.frame_gauche.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.frame_gauche.grid_columnconfigure((1, 2), weight=1)
        self.frame_gauche.grid_rowconfigure(5, weight=1)

        self.frame_milieu = customtkinter.CTkFrame(self, corner_radius=5)
        self.frame_milieu.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=(5, 5), pady=10)
        self.frame_milieu.grid_columnconfigure(0, weight=0)
        self.frame_milieu.grid_rowconfigure((0, 1), weight=1)

        self.frame_droite = customtkinter.CTkFrame(self, corner_radius=5)
        self.frame_droite.grid(row=0, column=2, rowspan=3, sticky="nsew", padx=(5, 10), pady=10)
        self.frame_droite.grid_columnconfigure(0, weight=1)
        self.frame_droite.grid_rowconfigure(3, weight=1)

        # Création des éléments de la frame gauche :
        self.label_airport = customtkinter.CTkLabel(self.frame_gauche, text="Code de l'aéroport de départ")
        self.label_airport.grid(row=0, column=0, columnspan=3, sticky="nsw", padx=10, pady=(5, 0))

        self.input_airport = customtkinter.CTkEntry(self.frame_gauche, placeholder_text="ex : KJFK")
        self.input_airport.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0, 5))
        self.input_airport.bind("<KeyRelease>", self.check_text_airport)

        # prochainement remplacé par un calendrier plus facile d'utilisation
        self.label_date = customtkinter.CTkLabel(self.frame_gauche, text="Selectionnez la date")
        self.label_date.grid(row=2, column=0, sticky="nsw", padx=10, pady=(5, 0))

        self.input_date = customtkinter.CTkEntry(self.frame_gauche, placeholder_text="aaaa/mm/jj")
        self.input_date.grid(row=3, column=0, sticky="nsew", padx=(10, 0), pady=(0, 5))
        self.input_date.bind("<KeyRelease>", self.check_text_date)

        self.input_heure_debut = customtkinter.CTkEntry(self.frame_gauche, placeholder_text="de : 13:00")
        self.input_heure_debut.grid(row=3, column=1, sticky="nsew", padx=5, pady=(0, 5))
        self.input_heure_debut.bind("<KeyRelease>", self.check_text_heure_debut)

        self.input_heure_fin = customtkinter.CTkEntry(self.frame_gauche, placeholder_text="à : 15:30")
        self.input_heure_fin.grid(row=3, column=2, sticky="nsew", padx=(0, 10), pady=(0, 5))
        self.input_heure_fin.bind("<KeyRelease>", self.check_text_heure_fin)
        self.input_heure_fin.configure(state="disabled")

        self.button_search = customtkinter.CTkButton(self.frame_gauche, corner_radius=5, text="Rechercher",
                                                     command=self.button_search_event)
        self.button_search.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0, 5))

        self.scroframe_liste_vols = customtkinter.CTkScrollableFrame(self.frame_gauche)
        self.scroframe_liste_vols.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.scroframe_liste_vols.grid_columnconfigure((0, 1), weight=1)

        # Configuration de la frame du milieu
        # On ajoute la map
        self.map_widget = TkinterMapView(self.frame_milieu, corner_radius=10, width=700)
        self.map_widget.grid(row=0, rowspan=2, sticky="nswe", padx=10, pady=10)
        self.map_widget.set_position(48.860381, 2.338594)
        self.map_widget.set_zoom(5)

        # Ajouter un rectangle avec les infos du vol sur la mapview
        # (obtenu en fouillant dans la librairie retro-Engineering au plus bas level possible)
        position_info = (435, 460)
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
                                                                 fill="", outline="",
                                                                 tag="button")

        self.canvas_text = self.map_widget.canvas.create_text(math.floor(position_info[0] + 10),
                                                              math.floor(position_info[1] + 11),
                                                              anchor="nw",
                                                              fill="white",
                                                              tag="button",
                                                              font=('Arial', 11, "bold"))
        # Ajouter cadre gradient couleur/altitude :
        position_info = (610, 15)
        width_infos = 75
        height_infos = 250
        self.canvas_rect_gradient_fond = self.map_widget.canvas.create_polygon(position_info[0], position_info[1],
                                                                               position_info[0] + width_infos,
                                                                               position_info[1],
                                                                               position_info[0] + width_infos,
                                                                               position_info[1] + height_infos,
                                                                               position_info[0],
                                                                               position_info[1] + height_infos,
                                                                               width=10,
                                                                               fill="", outline="",
                                                                               tag="button")
        # Ajout du curseur de selection de temps pendant le vol

        self.frame_curseur_temps = customtkinter.CTkFrame(self.frame_milieu)
        self.frame_curseur_temps.grid(row=2, sticky="nswe", padx=20, pady=10)
        self.frame_curseur_temps.grid_columnconfigure(1, weight=1)

        self.curseur_temps = customtkinter.CTkSlider(self.frame_curseur_temps, state="disabled", from_=2, to=100,
                                                     height=25, command=self.curseur_temps_event)
        self.curseur_temps.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.curseur_temps.set(10)

        self.label_temps_indicateur = customtkinter.CTkLabel(self.frame_curseur_temps, text="__:__", corner_radius=5,
                                                             fg_color="grey", padx="5", pady="5")
        self.label_temps_indicateur.grid(row=0, column=0, padx=(10, 0))

        # configuration de la frame de droite

        self.label_carbon_titre = customtkinter.CTkLabel(self.frame_droite, text="Calculateur\nCO2",
                                                         font=('Arial', 20, "bold"))
        self.label_carbon_titre.grid(row=0, column=0, padx=10, pady=(10,5))

        self.optionmenu_seat_class = customtkinter.CTkOptionMenu(self.frame_droite,
                                                                 values=["économique", "économique premium", "affaires",
                                                                         "première"],
                                                                 command=self.check_optionmenu_seat_class)
        self.optionmenu_seat_class.grid(row=1, column=0, sticky="swe", padx=10, pady=10)

        self.frame_actuelle_emission = customtkinter.CTkFrame(self.frame_droite)
        self.frame_actuelle_emission.grid(row=2, sticky="nswe", padx=10, pady=10)
        self.frame_actuelle_emission.grid_columnconfigure(0, weight=1)

        self.label_carbon_resultat = customtkinter.CTkLabel(self.frame_actuelle_emission, text="émission carbone :")
        self.label_carbon_resultat.grid(row=1, column=0, padx=5, pady=5)

        self.frame_compare_emission = customtkinter.CTkFrame(self.frame_droite)
        self.frame_compare_emission.grid(row=3, sticky="nswe", padx=10, pady=(0, 10))
        self.frame_compare_emission.grid_columnconfigure(0, weight=1)
        self.frame_compare_emission.grid_rowconfigure(1, weight=1)

        self.tabview_modele = customtkinter.CTkTabview(self.frame_compare_emission)
        self.tabview_modele.grid(row=0, column=0, sticky="swe", padx=10, pady=10)

        self.button_export_data = customtkinter.CTkButton(self.frame_compare_emission, text="Exporter")
        self.button_export_data.grid(row=2, column=0, sticky="swe", padx=10, pady=(5,10))

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

        # On vérifie que les caractères entrés sont des chiffres
        if 1 <= lenght < 11 and lenght != 5 and lenght != 8:
            if not self.input_date.get()[lenght - 1].isnumeric():
                self.input_date.delete(lenght - 1)

        # On s'assure de ne pas dépasser la taille maximale de la date
        if lenght >= 11:
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
                self.input_heure_debut.insert(lenght - 1, ':')

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
                self.input_heure_fin.insert(lenght - 1, ':')

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
            heure_fin = int(self.input_heure_fin.get()[:2]) + int(self.input_heure_fin.get()[3:5]) / 100
            heure_debut = int(self.input_heure_debut.get()[:2]) + int(self.input_heure_debut.get()[3:5]) / 100
            if heure_fin <= heure_debut + 0.30:
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
        self.index_vol = index
        self.optionmenu_seat_class.set("économique")
        self.liste_emissions = [[], [[]], [[]]]

        # On supprime les tabs de la zone de tabview pour en afficher par la suite de nouveaux
        if len(self.liste_modele_sim) > 0:
            for nom in self.liste_modele_sim:
                self.tabview_modele.delete(nom)

        # Récupération des données de trajectoire et formatage
        self.traj = airplane_traj(index - 1)
        traj = [x[1:3] for x in self.traj]

        # On attribue au bouton exporter la commande quand le vol est sélectionné
        self.button_export_data.configure(command=self.export_event)
        # Affichage du marqueur sous la forme d'un avion
        if self.marker_avion is not None:
            self.marker_avion.delete()
        rotated_pil_img = self.avion_image.rotate(self.traj[0][4])
        tk_icon = ImageTk.PhotoImage(rotated_pil_img)
        self.marker_avion = self.map_widget.set_marker(self.traj[-1][1], self.traj[-1][2], icon=tk_icon)
        self.marker_avion.change_icon(tk_icon)

        # Affichage de la trajectoire du vol sur la map
        self.map_widget.delete_all_path()
        self.map_widget.set_position((max(traj)[0] + min(traj)[0]) / 2,
                                     (max(traj, key=lambda x: x[1])[1] + min(traj, key=lambda x: x[1])[1]) / 2)

        for i in range(len(traj) - 1):
            altitude_moy = (self.traj[i][3] + self.traj[i + 1][3]) / 2
            couleur_R = int(459 - (204 / 6250) * altitude_moy)
            if couleur_R > 255:
                couleur_R = 255
            elif couleur_R < 0:
                couleur_R = 0
            couleur_G = int(229 + ((128 - 229) / 6250) * altitude_moy)
            if couleur_G < 0:
                couleur_G = 0

            couleur_B = int(204 - (204 / 6250) * altitude_moy)
            if couleur_B < 0:
                couleur_B = 0
            self.map_widget.set_path([traj[i], traj[i + 1]],
                                     color='#{:02x}{:02x}{:02x}'.format(*(couleur_R, couleur_G, couleur_B)), width=3)

        # Adaptation du curseur au vol selectionné
        self.curseur_temps.configure(state="normal")
        self.curseur_temps.configure(to=len(self.traj))

        # Mise à jour de l'encadré altitude (gradient)
        if self.map_widget.canvas.itemcget(self.canvas_rect_gradient_fond, 'fill') != "gray25":
            self.map_widget.canvas.itemconfig(self.canvas_rect_gradient_fond, fill="gray25", outline="gray25")
            for x in range(0, 12500, 100):
                position_gradient = (615, 255 - x * 235 / 12500)
                width_infos = 15
                height_infos = 2

                couleur_R = int(459 - (204 / 6250) * x)
                if couleur_R > 255:
                    couleur_R = 255
                elif couleur_R < 0:
                    couleur_R = 0
                couleur_G = int(229 + ((128 - 229) / 6250) * x)
                if couleur_G < 0:
                    couleur_G = 0

                couleur_B = int(204 - (204 / 6250) * x)
                if couleur_B < 0:
                    couleur_B = 0

                self.map_widget.canvas.create_polygon(position_gradient[0], position_gradient[1],
                                                      position_gradient[0] + width_infos,
                                                      position_gradient[1],
                                                      position_gradient[0] + width_infos,
                                                      position_gradient[1] + height_infos,
                                                      position_gradient[0],
                                                      position_gradient[1] + height_infos,
                                                      width=10,
                                                      fill='#{:02x}{:02x}{:02x}'.format(
                                                          *(couleur_R, couleur_G, couleur_B)),
                                                      tag="button")
                if x % 2000 == 0:
                    self.map_widget.canvas.create_text(math.floor(position_gradient[0] + 20),
                                                       math.floor(position_gradient[1] - 5),
                                                       anchor="nw",
                                                       fill="white",
                                                       tag="button",
                                                       font=('Arial', 11, "bold"),
                                                       text=str(x) + "m")
        # Mise à jour de l'encadré montrant les informations du vol
        self.map_widget.canvas.itemconfig(self.canvas_rect, fill="gray25", outline="gray25")
        self.map_widget.canvas.itemconfig(self.canvas_text,
                                          text=f"Compagnie : {self.liste_vols["compagnie"].values[index - 1]}\n"
                                               f"Aéroport de départ : {self.liste_vols["estDepartureAirport"].values[
                                                   index - 1]}\n"
                                               f"Aéroport d'arrivée : {self.liste_vols["estArrivalAirport"].values[
                                                   index - 1]}\n"
                                               f"Call sign : {self.liste_vols["callsign"].values[index - 1]}\n"
                                               f"Numéro ICAO24 : {self.liste_vols["icao24"].values[index - 1]}\n"
                                               f"Heure de départ : {timestamp_to_date(self.liste_vols["firstSeen"].
                                                                                      values[index - 1])[11:16]}\n"
                                               f"Heure d'arrivée : {timestamp_to_date(self.liste_vols["lastSeen"].values
                                                                                      [index - 1])[11:16]}\n")

        # Envoie des données de vol au calculateur CO2
        modele_red = self.liste_vols["modelReduit"].values[index - 1]

        value_emmi = format(round(self.calculer_carbon(modele_red,
                                                calcule_distance(self.traj), calcule_duree(self.traj),
                                                self.liste_vols["uid"].values[index - 1],
                                                motors_nb=self.liste_vols["numberEngine"].values[index - 1],
                                                seat_class="économique") / 1000, 3), ".3f")
        self.label_carbon_resultat.configure(
            text=f'émission CO2 du vol\npar passager\n{value_emmi} tonnes de CO2')
        modele_engine = {'uid': [self.liste_vols["uid"].values[index-1]], 'modelEngine': [self.liste_vols["modelEngine"].values[index-1]]}
        self.liste_moteurs_sim = pd.DataFrame(data=modele_engine)
        self.liste_moteurs_sim = pd.concat([self.liste_moteurs_sim, similar_engines(self.liste_vols["uid"].values[index - 1])])

        self.liste_modele_sim = [modele_red]
        self.liste_modele_sim = self.liste_modele_sim + similar_models(modele_red)
        j=0
        for modele_red in self.liste_modele_sim:
            self.tabview_modele.add(modele_red)
            i = 0
            for moteur in self.liste_moteurs_sim.itertuples():
                check_avions_compare_var = customtkinter.StringVar(value="on")
                modele_moteur = moteur.modelEngine
                emission = format(round(
                    self.calculer_carbon(modele_red, calcule_distance(self.traj),
                                         calcule_duree(self.traj), moteur.uid,
                                         motors_nb=self.liste_vols["numberEngine"].values[index - 1],
                                         seat_class="économique") / 1000, 3), ".3f")
                check_avions_compare = customtkinter.CTkCheckBox(self.tabview_modele.tab(modele_red),
                                                                 text=f'engine {modele_moteur.split(' ')[0]} : {emission} t',
                                                                 variable=check_avions_compare_var, onvalue="on",
                                                                 offvalue="off")
                check_avions_compare.grid(row=i, sticky="nsw", padx=10, pady=10)
                self.liste_emissions[1][j].append(modele_moteur)
                self.liste_emissions[2][j].append(emission)
                i += 1
            self.liste_emissions[0].append(modele_red)
            self.liste_emissions[1].append([])
            self.liste_emissions[2].append([])

            j += 1
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
                                                      f"{vol.estArrivalAirport} : {timestamp_to_date(vol.firstSeen)[
                                                                                   11:16]}-"
                                                      f"{timestamp_to_date(vol.lastSeen)[11:16]}",
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
        self.label_temps_indicateur.configure(text=timestamp_to_date(self.traj[value - 1][0])[11:16])

        # Rotation du marqueur et déplacement de ce-dernier
        rotated_pil_img = self.avion_image.rotate(-self.traj[value - 1][4])
        tk_icon = ImageTk.PhotoImage(rotated_pil_img)
        self.marker_avion.change_icon(tk_icon)
        self.marker_avion.set_position(self.traj[value - 1][1], self.traj[value - 1][2])

        # Mise à jour du tracé de la trajectoire
        self.map_widget.delete_all_path()
        self.map_widget.set_path(traj[0:value], color="#242424", width=3)

    def check_optionmenu_seat_class(self, choice):
        seat_class = choice
        self.liste_emissions = [[], [[]], [[]]]

        value_emmi = format(round(self.calculer_carbon(self.liste_vols["modelReduit"].values[self.index_vol - 1],
                                                calcule_distance(self.traj), calcule_duree(self.traj),
                                                self.liste_vols["uid"].values[self.index_vol - 1],
                                                motors_nb=self.liste_vols["numberEngine"].values[self.index_vol - 1],
                                                seat_class=seat_class) / 1000, 3), ".3f")
        self.label_carbon_resultat.configure(
            text=f'émission CO2 du vol\npar passager\n{value_emmi} tonnes de CO2')
        self.liste_emissions[1][0].append(self.liste_vols["modelEngine"].values[self.index_vol - 1])
        self.liste_emissions[2][0].append(value_emmi)

        j = 0
        for modele in self.liste_modele_sim:
            i = 0
            for element in self.tabview_modele.tab(modele).winfo_children():
                texte = element.cget("text")
                value = format(round(
                    self.calculer_carbon(modele,
                                         calcule_distance(self.traj), calcule_duree(self.traj),
                                         self.liste_moteurs_sim["uid"].values[i],
                                         motors_nb=self.liste_vols["numberEngine"].values[self.index_vol - 1],
                                         seat_class=seat_class) / 1000, 3), ".3f")
                element.configure(text=texte[0:len(texte) - 7] + str(value) + " t")
                self.liste_emissions[1][j].append(self.liste_moteurs_sim["modelEngine"].values[i])
                self.liste_emissions[2][j].append(value)
                i += 1
            self.liste_emissions[0].append(modele)
            self.liste_emissions[1].append([])
            self.liste_emissions[2].append([])
            j += 1

    def export_event(self):
        compteur = 0
        liste_emission = [self.liste_emissions[0], [[self.liste_emissions[1][0][0]]], [[self.liste_emissions[2][0][0]]]]
        j = 0
        for modele in self.liste_modele_sim:
            i = 0
            for element in self.tabview_modele.tab(modele).winfo_children():
                if element.get() == "on":
                    compteur += 1
                    liste_emission[1][j].append(self.liste_emissions[1][j][i])
                    liste_emission[2][j].append(self.liste_emissions[2][j][i])
                i += 1
            liste_emission[1].append([])
            liste_emission[2].append([])
            j += 1

        somme_totale = compteur
        while somme_totale > 6 :
            somme_totale = 0
            nombre = 0
            plus_grande_len = 0
            for i in range(len(liste_emission[0])):
                somme_totale += len(liste_emission[1][i])
                if len(liste_emission[1][i]) >= nombre:
                    nombre = len(liste_emission[1][i])
                    plus_grande_len = i
            if plus_grande_len == 0 :
                (maxi, indice) = find_max_number([0] + liste_emission[2][plus_grande_len][1:len(liste_emission[2][plus_grande_len])])
            else : 
                (maxi, indice) = find_max_number(liste_emission[2][plus_grande_len])

            del liste_emission[1][plus_grande_len][indice]
            del liste_emission[2][plus_grande_len][indice]
        self.save_map_as_png("FlightRadar/Interface/map.png")
        pdf = Pdf(map_chemin="FlightRadar/Interface/map.png", classe = self.optionmenu_seat_class.get())
        vol = self.liste_vols.values[self.index_vol - 1]
        vol = np.append(vol, calcule_distance(self.traj))
        vol[5] = timestamp_to_date(vol[5])
        vol[6] = timestamp_to_date(vol[6])
        pdf.set_data(vol, liste_emission)
        pdf.generer_pdf()

    def calculer_carbon(self, modele, distance, duration, uid, motors_nb, seat_class):
        """
        Cette procédure est déclenchée à l'exécution de :func:button_vol_event et permet de récupérer l'émission
        carbone d'un modèle d'avion donné pour la distance parcourue et l'affiche dans la zone dédiée.

        :param str modele: Nom du modèle d'avion (ex : B777)
        :param float distance: Valeur de la distance parcourue calculée à l'aide de la fonction :func:calcule_distance.
        """
        value = passenger_carbon_emissions(distance, duration, modele, uid, motors_nb, seat_class)
        return value

    def save_map_as_png(self, file_path):
        widget = self.map_widget
        x = widget.winfo_rootx()
        y = widget.winfo_rooty()
        width = x + widget.winfo_width()
        height = y + widget.winfo_height()
        img = ImageGrab.grab(bbox=(x, y, width, height))
        img.save(file_path)


def timestamp_to_date(timestamp):
    """
    Cette fonction permet de convertir un timestamp unix en date GMT.

    :param int timestamp: Valeur du timestamp à convertir
    :returns: String représentant la valeur de la date correspondant au timestamp d'origine
    :rtype: str
    """
    return str(datetime.datetime.fromtimestamp(timestamp))


def date_to_timestamp(date):  # En construction
    return


def calcule_distance(traj):
    """
    Calcule la distance totale parcourue sur une trajectoire donnée.

    Cette fonction utilise la formule de Haversine pour calculer la distance entre chaque point successif de la trajectoire.

    :param list traj: Liste de points de la trajectoire où chaque point est une liste ou un tuple
                      contenant le temps en UNIX, la latitude, la longitude, et un indicateur optionnel de validité.

    :return: La distance totale parcourue en kilomètres.
    :rtype: float
    """
    somme = 0
    for i in range(len(traj) - 1):
        lat1 = traj[i][1]
        lon1 = traj[i][2]
        lat2 = traj[i + 1][1]
        lon2 = traj[i + 1][2]
        deltalat = lat2 - lat1
        deltalon = lon2 - lon1
        d = 2 * 6371 * math.asin(math.sqrt(math.sin(math.radians(deltalat / 2)) ** 2 + math.cos(math.radians(lat1)) *
                                           math.cos(math.radians(lat2)) * math.sin(math.radians(deltalon / 2)) ** 2))
        somme += d
    return somme


def calcule_duree(traj):
    """
    Calcule la durée totale d'une trajectoire donnée.

    Cette fonction somme les différences de temps entre chaque point successif de la trajectoire.

    :param list traj: Liste de points de la trajectoire où chaque point est une liste ou un tuple
                      contenant le temps en UNIX, la latitude, la longitude, et un indicateur optionnel de validité.

    :return: La durée totale de la trajectoire en secondes.
    :rtype: int
    """
    duree = 0
    for i in range(len(traj) - 1):
        if traj[i][3] and traj[i + 1][3]:
            duree += traj[i + 1][0] - traj[i][0]
    return duree

def find_max_number(liste_de_nombres):
    maxi = 0
    indice = 0
    for i in range(len(liste_de_nombres)):
        if float(liste_de_nombres[i]) >= maxi:
            maxi = float(liste_de_nombres[i])
            indice  = i

    return maxi, indice
