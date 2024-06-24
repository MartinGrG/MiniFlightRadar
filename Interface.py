""" Ce script défini la classe interface. Cet objet correspond à une fenêtre
pop up permettant à l'utilisateur d'intéragir avec le code. """


import customtkinter
from tkintermapview import TkinterMapView
import datetime
import time
from DataBase import sortie, airplane_traj
import pandas as pd


customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"

class Interface(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        self.liste_vols = pd.DataFrame({})
        self.airport_depart = ''
        self.map_traj = None
        self.traj = []
        # configuration de la fenêtre :
        self.title("Panneau usager")  # titre
        self.geometry("1300x600")  # dimensions de la fenètre
        self.attributes('-topmost', True)  # on fait passer la fenètre au-dessus du reste à l'apparition

        # configuration de la grille de base (1x3) :
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # création des frames de l'interface :
        self.frame_gauche = customtkinter.CTkFrame(self, corner_radius=5)
        self.frame_gauche.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.frame_gauche.grid_columnconfigure((1,2), weight=1)
        self.frame_gauche.grid_rowconfigure(5, weight=1)

        self.frame_milieu = customtkinter.CTkFrame(self, corner_radius=5)
        self.frame_milieu.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=10, pady=10)
        self.frame_milieu.grid_columnconfigure(0, weight=1)
        self.frame_milieu.grid_rowconfigure((0, 1), weight=1)

        self.frame_droite = customtkinter.CTkFrame(self, corner_radius=5)
        self.frame_droite.grid(row=0, column=2, rowspan=3, sticky="nsew", padx=10, pady=10)
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

        self.curseur_temps = customtkinter.CTkSlider(self.frame_curseur_temps,state="disabled", from_=0, to=100, height=25, command=self.curseur_temps_event)
        self.curseur_temps.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.curseur_temps.set(10)

        self.label_temps_indicateur = customtkinter.CTkLabel(self.frame_curseur_temps, text="13h46", corner_radius=5, fg_color="grey", padx="5", pady="5")
        self.label_temps_indicateur.grid(row=0, column=0, padx=(10,0))

        # configuration de la frame de droite

        self.label_carbon_titre = customtkinter.CTkLabel(self.frame_droite, text="Calculateur\nCO2", font=('Arial', 25, "bold"))
        self.label_carbon_titre.grid(row=0,column=0, padx=10, pady=10)

        self.frame_actuelle_emission = customtkinter.CTkFrame(self.frame_droite)
        self.frame_actuelle_emission.grid(row=1, sticky="nswe", padx=10, pady=10)
        self.frame_actuelle_emission.grid_columnconfigure(0, weight=1)

        self.label_carbon_resultat = customtkinter.CTkLabel(self.frame_actuelle_emission, text="Ce vol a émis\n 500kg de CO2")
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

    def check_text_airport(self,event):
        lenght = len(self.input_airport.get())

        if (lenght >= 1):
            if (self.input_airport.get()[lenght - 1].isnumeric()):
                self.input_airport.delete(lenght - 1)
        if (lenght >= 5):
            self.input_airport.delete(lenght - 1)

    def check_text_date(self,event):
        lenght = len(self.input_date.get())
        if (lenght >= 1 and lenght != 5 and lenght !=8):
            if (not self.input_date.get()[lenght - 1].isnumeric()):
                self.input_date.delete(lenght - 1)
        if (lenght == 4 or lenght == 7):
            self.input_date.insert(lenght, '/')
        if (lenght >= 11):
            self.input_date.delete(lenght - 1)

    def check_text_heure_debut(self,event):
        lenght = len(self.input_heure_debut.get())

        if (lenght >= 1 and lenght != 3):
            if (not self.input_heure_debut.get()[lenght - 1].isnumeric()):
                self.input_heure_debut.delete(lenght - 1)
        if (lenght == 2):
            self.input_heure_debut.insert(lenght, ':')
        if (lenght == 4 and int(self.input_heure_debut.get()[lenght - 1]) >= 6):
            self.input_heure_debut.delete(lenght - 1)
        if (lenght >= 6):
            self.input_heure_debut.delete(lenght - 1)
        if (lenght < 5):
            self.input_heure_fin.delete(0, 5)
            self.input_heure_fin.configure(state="disabled")
        else:
            self.input_heure_fin.configure(state="normal")
    def check_text_heure_fin(self, event):
        lenght = len(self.input_heure_fin.get())

        if (lenght >= 1 and lenght != 3):
            if (not self.input_heure_fin.get()[lenght - 1].isnumeric()):
                self.input_heure_fin.delete(lenght - 1)
        if (lenght == 2):
            self.input_heure_fin.insert(lenght, ':')
        if (lenght >= 6):
            self.input_heure_fin.delete(lenght - 1)
        if (lenght ==4 and int(self.input_heure_fin.get()[lenght - 1]) >= 6):
            self.input_heure_fin.delete(lenght - 1)
        if (lenght == 5):
            heure_fin = int(self.input_heure_fin.get()[:2]) + int(self.input_heure_fin.get()[3:5])/100
            heure_debut = int(self.input_heure_debut.get()[:2]) + int(self.input_heure_debut.get()[3:5])/100
            if (heure_fin <= heure_debut+0.30):
                self.input_heure_fin.delete(0, 5)


    def button_vol_event(self, index):
        vol_traj = airplane_traj(index)
        print(vol_traj[-1])
        self.traj = [x[1:3] for x in vol_traj]

        self.map_widget.delete_all_path()
        self.map_traj = self.map_widget.set_position(self.traj[0][0], self.traj[0][1])
        self.map_widget.set_path(self.traj, color="red", width=3)
        self.curseur_temps.configure(state="normal")
        self.curseur_temps.configure(to=len(self.traj))

    def button_search_event(self):
        etat = (len(self.input_heure_fin.get()) == 5 and len(self.input_heure_debut.get()) == 5 and
                len(self.input_airport.get()) == 4 and len(self.input_date.get()) == 10)
        if etat:
            airport = self.input_airport.get().upper()
            date_debut = self.input_date.get() + " " + self.input_heure_debut.get()
            date_fin = self.input_date.get() + " " + self.input_heure_fin.get()
            timestamp_debut = int(time.mktime(datetime.datetime.strptime(date_debut, "%Y/%m/%d %H:%M").timetuple()))
            timestamp_fin = int(time.mktime(datetime.datetime.strptime(date_fin, "%Y/%m/%d %H:%M").timetuple()))
            print(timestamp_debut,timestamp_fin)
            #self.liste_vols = sortie(airport, timestamp_debut, timestamp_fin)

            for widget in self.scroframe_liste_vols.winfo_children():
                widget.destroy()

            i = 0

            for vol in self.liste_vols.itertuples():
                button = customtkinter.CTkButton(self.scroframe_liste_vols, corner_radius=5, text=f"Vol {vol.estDepartureAirport}-{vol.estArrivalAirport} : {vol.firstSeen}", command=lambda index=vol.index: self.button_vol_event(index))
                button.grid(row=i, column=0, columnspan=2, sticky="nsew", pady=1)
                i+=1
        else:
            print("Attention remplissez tous les champs")



    def curseur_temps_event(self, value):
        self.label_temps_indicateur.configure(text=value)

        self.map_widget.delete_all_path()
        self.map_traj = self.map_widget.set_position(self.traj[0][0], self.traj[0][1])
        self.map_widget.set_path(self.traj[0:value], color="red", width=3)

    def checkbox_event(self):
        print("B777")

    def export_event(self):
        print("export")







