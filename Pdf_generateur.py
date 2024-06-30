""" Ce script décrit l'objet PDF et donne les fonctions associées"""
from fpdf import FPDF
import matplotlib.pyplot as plt


class Pdf(FPDF):
    titre = "Titre par défaut"
    infos_vol = ["index","callsign","AAAA","AAAA","icao24","aaaa/mm/jj he:mi:se","aaaa/mm/jj he:mi:se","compagnie","codeModel","codeEngine","model","modelReduit","modelEngine","uid","1000"]
    infos_emission = [["engine1_test","engine2_test","engine3_test","CF34-8C5","engine5"],[0.1,0.2,0.3,0.7,1.2]]
    graphique_emission = ""
    map_chemin = ""

    def __init__(self, map_chemin):
        super().__init__(orientation="portrait", unit="mm", format="A4", font_cache_dir="DEPRECATED")
        self.add_page()
        self.map_chemin = map_chemin
        self.set_margins(25.4, 12.7, 12.7)

    def set_data(self, infos_vol, emission):
        self.infos_vol = infos_vol
        self.infos_emission = emission
        self.titre = f"Compte rendu du vol : {self.infos_vol[3]} - {self.infos_vol[2]}"

    def generer_graphique(self):
        x = self.infos_emission[0]
        y = self.infos_emission[1]
        plt.title(f"émission du {self.infos_vol[11]} pour le vol sélectionné\navec différents moteurs")
        plt.xlabel("Noms des moteurs")
        plt.ylabel("Valeurs d'émission CO2 par personne (kg)")
        plt.bar(x, y)
        repertoire = "Interface/graphique_emission.png"
        plt.savefig(repertoire)
        return repertoire

    def en_tete(self, texte):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, texte, 0, 1, 'C')

    def pied_de_page(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def titre_chapitre(self, titre):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, titre, 0, align='L')
        self.ln()

    def corps_chapitre(self, corps):
        self.set_font('helvetica', '', 12)
        self.multi_cell(0, 10, corps)
        self.ln()

    def ajouter_image(self, chemin_image, x, y, taille):
        self.image(chemin_image, x=x, y=y, w=taille)

    def ajouter_tableau(self, donnees):
        nombre = len(donnees[0])
        taille_max = 90/nombre
        self.set_font('helvetica', 'B', 10)
        for element in donnees[0]:
            self.cell(taille_max, 10, str(element), 1, align='C')
        self.ln()

        self.set_font('helvetica', '', 11)
        for element in donnees[1]:
            self.cell(taille_max, 10, str(element), 1, align='C')
        self.ln()

    def ajouter_separateur(self):
        self.ln(5)
        self.cell(0, 0, '', 'T')
        self.ln(5)
    
    def generer_pdf(self):
        # En-tête et pied de page personnalisés
        self.alias_nb_pages()
        self.set_auto_page_break(auto=True)
        
        # Titre principal
        self.set_font('helvetica', 'B', 16)
        self.cell(self.get_string_width('FICHE DE VOL :')+2, 10, 'FICHE DE VOL :', 0)

        self.set_font('helvetica', '', 12)
        self.cell(0, 10, text=self.infos_vol[7] + ' ' + self.infos_vol[1], border=0)
        self.ln(7)

        self.set_font('helvetica', 'I', 12)
        self.cell(0, 10, self.infos_vol[5][0:10], 0, align='L')
        self.ln(10)

        # Section d'information
        long_page = self.w-25.4-12.7

        self.set_font('helvetica', '', 11)
        x_i = self.x
        y_i = self.y
        self.cell(long_page-self.get_string_width(self.infos_vol[9])-5, 10, text=self.infos_vol[10]+' ('+self.infos_vol[11]+')', align='L')
        self.cell(self.get_string_width('Moteur'), h=10, text='Moteur :', align='L')
        self.ln(5)
        self.set_font('helvetica', 'B', 11)
        self.cell(self.get_string_width(self.infos_vol[3]+' : '), 10, text=self.infos_vol[3]+' : ')
        self.set_font('helvetica', '', 11)
        self.cell(long_page-self.get_string_width(self.infos_vol[9])-self.get_string_width(self.infos_vol[3]+' : ')-5, 10, text=self.infos_vol[5][11:16])
        self.cell(self.get_string_width(self.infos_vol[9]), h=10, text=self.infos_vol[9], align='L')
        x_f = long_page+25.4
        self.ln(5)
        self.set_font('helvetica', 'B', 11)
        self.cell(self.get_string_width(self.infos_vol[2] + ' : '), 10, text=self.infos_vol[2] + ' : ')
        self.set_font('helvetica', '', 11)
        self.cell(long_page-self.get_string_width(self.infos_vol[9])-self.get_string_width(self.infos_vol[2]+' : ')-5, 10, text=self.infos_vol[6][11:16])
        self.cell(self.get_string_width(self.infos_vol[-3]), h=10, text=self.infos_vol[-3], align='L')
        self.ln(5)
        self.cell(long_page-self.get_string_width(self.infos_vol[9])-5, 10, text='Distance parcourue :'+str(round(float(self.infos_vol[-1]), 1))+'km')

        self.ln()
        y_f = self.y
        self.cell(self.get_string_width('icao24')+3, 10, 'icao24', border=1)
        self.cell(0, 10, text=self.infos_vol[4], border=1, align='L')

        self.ln(10)
        self.rect(x_i, y_i, x_f-x_i, y_f-y_i)
        self.rect(x_i + long_page-self.get_string_width(self.infos_vol[9])-5, y_i, x_f - x_i - (long_page-self.get_string_width(self.infos_vol[9])-5), y_f - y_i)

        self.ln(5)
        # Image

        x_i = self.x
        y_i = self.y

        self.ajouter_image(self.map_chemin, 25.4, None, long_page)
        y_f = self.y
        self.set_line_width(0.5)  # Épaisseur de trait de 2 points
        self.rect(x_i, y_i, long_page, y_f-y_i)
        self.set_line_width(0.2)  # Épaisseur de trait de 2 points

        # Séparateur
        self.ajouter_separateur()

        y_i = self.y
        # Nouveau titre
        self.titre_chapitre('Emission CO2 du vol (en kg par passager)')

        # Image
        self.ajouter_image(self.generer_graphique(), 115, y_i, 90)

        self.ln(5)
        # Tableau
        donnees = self.infos_emission
        self.ajouter_tableau(donnees)

        # Enregistrer le PDF
        self.output("Compte_rendu.pdf")
        del self