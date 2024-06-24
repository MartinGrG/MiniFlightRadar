""" Ce script défini la classe interface. Cet objet correspond à une fenêtre
pop up permettant à l'utilisateur d'intéragir avec le code. """


import customtkinter
from tkintermapview import TkinterMapView


customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"

class Interface(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        self.airport_depart = ''

        # configuration de la fenêtre :
        self.title("Panneau usager")  # titre
        self.geometry("1300x600")  # dimensions de la fenètre
        self.attributes('-topmost', True)  # on fait passer la fenètre au-dessus du reste à l'apparition

        # configuration de la grille de base (1x3) :
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # création des frames de l'interface :
        self.frame_gauche = customtkinter.CTkFrame(self, corner_radius=5)
        self.frame_gauche.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=10, pady=10)
        self.frame_gauche.grid_columnconfigure(0, weight=1)

        self.frame_milieu = customtkinter.CTkFrame(self, corner_radius=5)
        self.frame_milieu.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=10, pady=10)
        self.frame_milieu.grid_columnconfigure(0, weight=1)
        self.frame_milieu.grid_rowconfigure((0, 1), weight=1)

        self.frame_droite = customtkinter.CTkFrame(self, corner_radius=5)
        self.frame_droite.grid(row=0, column=2, rowspan=3, sticky="nsew", padx=10, pady=10)
        self.frame_droite.grid_columnconfigure(0,weight=1)

        # Création des éléments de la frame gauche :
        self.airport_label = customtkinter.CTkLabel(self.frame_gauche, text="Code de l'aéroport de départ")
        self.airport_label.grid(row=0, column=0, columnspan=2, sticky="nsw", padx=10, pady=(5,0))

        self.airport_input = customtkinter.CTkEntry(self.frame_gauche, placeholder_text="ex : AX500")
        self.airport_input.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0,5))

        # prochainement remplacé par un calendrier plus facile d'utilisation
        self.date_label = customtkinter.CTkLabel(self.frame_gauche, text="Selectionnez la date")
        self.date_label.grid(row=2, column=0, sticky="nsw", padx=10, pady=(5, 0))

        self.date_input = customtkinter.CTkEntry(self.frame_gauche, placeholder_text="aaaa/mm/jj")
        self.date_input.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 5))

        self.search_button = customtkinter.CTkButton(self.frame_gauche, corner_radius=5, fg_color="grey", text="Rechercher", command=self.button_search_event)
        self.search_button.grid(row=3, column=1, sticky="nsew", padx=(0,10), pady=(0, 5))

        self.liste_vols = customtkinter.CTkScrollableFrame(self.frame_gauche, height=400)
        self.liste_vols.grid(row=4,column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.liste_vols.grid_columnconfigure((0,1), weight=1)

        for i in range(20):
            button = customtkinter.CTkButton(self.liste_vols, corner_radius=5, fg_color="grey", text=f"Vol n°{i}", command=lambda code=i: self.button_vol_event(code))
            button.grid(row=i, column=0, columnspan=2, sticky="nsew", pady=1)

        # configuration de la frame du milieu
        # On ajoute la map
        self.map_widget = TkinterMapView(self.frame_milieu, corner_radius=10, width=700)
        self.map_widget.grid(row=0, rowspan=2, sticky="nswe", padx=10, pady=10)
        self.map_widget.set_position(48.860381, 2.338594)
        self.map_widget.set_zoom(5)

        # Ajout du curseur de selection de temps pendant le vol

        self.frame_curseur_temps = customtkinter.CTkFrame(self.frame_milieu)
        self.frame_curseur_temps.grid(row=2,sticky="nswe", padx=20,pady=10)
        self.frame_curseur_temps.grid_columnconfigure(1, weight=1)

        self.curseur_temps = customtkinter.CTkSlider(self.frame_curseur_temps, from_=0, to=100, height=25, command=self.curseur_temps_event)
        self.curseur_temps.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.curseur_temps.set(10)

        self.temps_indicateur_label = customtkinter.CTkLabel(self.frame_curseur_temps, text="13h46", corner_radius=5, fg_color="grey", padx="5", pady="5")
        self.temps_indicateur_label.grid(row=0, column=0, padx=(10,0))

        # configuration de la frame de droite

        self.carbon_label = customtkinter.CTkLabel(self.frame_droite, text="Calculateur\nCO2")
        self.carbon_label.grid(row=0,column=0, padx=10)


    def button_vol_event(self, nbre):
        print(nbre)

    def button_search_event(self):
        print("hello")

    def curseur_temps_event(self, value):
        self.temps_indicateur_label.configure(text=value)
