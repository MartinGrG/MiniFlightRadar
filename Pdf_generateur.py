""" Ce script décrit l'objet PDF et donne les fonctions associées"""
from fpdf import FPDF
import matplotlib.pyplot as plt


class Pdf(FPDF):
    titre = "Titre par défaut"
    infos_vol = ["index","callsign","estArrivalAirport","estDepartureAirport","icao24","firstSeen","lastSeen","compagnie","codeModel","codeEngine","model","modelReduit","modelEngine","uid"]
    infos_emission = [["engine1_test","engine2_test","engine3_test"],[0.1,0.2,0.3]]
    graphique_emission = ""
    def __init__(self):
        super().__init__(orientation="portrait", unit="mm", format="A4", font_cache_dir="DEPRECATED")
        self.add_page()

    def generer_pdf(self):
        self.set_font('arial', size=12)
        self.cell(text=self.titre)
        self.image(self.graphique_emission)
        self.output("Compte_rendu.pdf")
        del self

    def set_data(self, infos_vol, emission):
        self.infos_vol = infos_vol
        self.infos_emission = emission
        self.titre = f"Compte rendu du vol : {self.infos_vol[3]} - {self.infos_vol[2]}"
        self.graphique_emission = self.generer_graphique(self.infos_emission)

    def generer_graphique(self):
        x = self.infos_emission[0]
        y = self.infos_emission[1]
        plt.title(f"émission du {self.infos_vol[11]} pour le vol sélectionné\npour différents moteurs")
        plt.xlabel("Noms des moteurs")
        plt.ylabel("Valeurs d'émission CO2 par personne (kg)")
        plt.bar(x, y)
        repertoire = "/Interface/graphique_emission.png"
        plt.savefig(repertoire)
        return repertoire


pdf = Pdf()

pdf.generer_pdf()




# fonction generer_pdf, set_data_pdf