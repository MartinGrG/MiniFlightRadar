""" Ce script décrit l'objet PDF et donne les fonctions associées"""
from fpdf import FPDF
import matplotlib.pyplot as plt

class Pdf(FPDF):
    """
    Cette classe étend les fonctionnalités de FPDF pour générer un document PDF personnalisé.

    :param titre: Titre du document PDF, par défaut "Titre par défaut".
    :type titre: Str
    :param infos_vol: Informations sur le vol sous forme de liste, contenant différents détails
            comme l'index, le callsign, les dates de départ et d'arrivée, la compagnie, le modèle d'avion, etc.
    :type infos_vol: list
    :param infos_emission: Informations sur les émissions de carbone, comprenant des données sur les moteurs,
            les émissions associées à chaque moteur, les modèles d'avions, etc.
    :type infos_emission: list
    :param graphique_emission: Chemin vers le graphique des émissions de carbone.
    :type graphique_emission: Str
    :param map_chemin: Chemin vers l'image de la carte capturée.
    :type map_chemin: Str
    :param classe: Classe de siège pour laquelle les émissions sont calculées, par exemple économique, affaires, etc.
    :type classe: Str
    """
    titre = "Titre par défaut"
    infos_vol = ["index", "callsign", "AAAA", "AAAA", "icao24", "aaaa/mm/jj 13:34:se", "aaaa/mm/jj 15:23:se",
                 "compagnie", "codeModel", "codeEngine", "model", "numberEngine", "modelReduit", "modelEngine", "uid",
                 "1000"]
    infos_emission = [['CL6', 'B777'], [["engine1_test", "engine2_test", "engine3_test"],
                                        ["engine1_test", "engine2_test"]],[[0.1, 0.6, 0.2], [0.1, 0.5]]]
    graphique_emission = ""
    map_chemin = ""
    classe = ''

    def __init__(self, map_chemin, classe):
        """
        Initialise l'objet Pdf avec les paramètres spécifiés.

        Ajoute une page au document et définit les marges et la classe du
        passager lors du vol.

        :param str map_chemin: Chemin de l'image de la carte du vol.
        :param str classe: Classe du passager lors du vol.
        """
        super().__init__(orientation="portrait", unit="mm", format="A4", font_cache_dir="DEPRECATED")
        self.add_page()
        self.map_chemin = map_chemin
        self.set_margins(12.7, 12.7, 12.7)
        self.classe = classe

    def set_data(self, infos_vol, emission):
        """
        Update les données du vol et les informations des émissions.

        :param list infos_vol: Liste contenant les informations du vol (ligne de flight_data.csv).
        :param list emission: Liste contenant les informations des émissions CO2 comparatives.
        """
        self.infos_vol = infos_vol
        self.infos_emission = emission
        self.titre = f"Compte rendu du vol : {self.infos_vol[3]} - {self.infos_vol[2]}"

    def generer_graphique(self):
        """
        Génère un graphique des émissions de CO2 pour le vol sélectionné.

        Le graphique est sauvegardé sous le chemin spécifié.

        :returns: Chemin du fichier du graphique généré.
        :rtype: Str
        """

        x = self.infos_emission[1]
        y = self.infos_emission[2]
        plt.title(f"émission pour le vol sélectionné\navec différents modèles et moteurs d'avions")
        plt.xlabel("Noms des moteurs")
        plt.ylabel("Valeurs d'émission CO2 par personne (t)")

        #on génère les barres d'émission CO2 pour chaque modèle d'avion.
        for i in range(len(self.infos_emission[0])) :
            x[i] = [f'({self.infos_emission[0][i]}){item}' for item in x[i]]
            y[i] = [float(y) for y in y[i]]
            plt.bar(x[i], y[i], label=self.infos_emission[0][i])

        # On écrit les labels abscisses de travers
        plt.xticks(rotation=15)
        plt.legend()

        # On sauvegarde le graphique pour l'afficher par la suite dans le pdf.
        plt.savefig("FlightRadar/Interface/graphique_emission.png")
        plt.close()
        return "FlightRadar/Interface/graphique_emission.png"

    def titre_chapitre(self, titre):
        """
        Ajoute un titre de chapitre au PDF avec le titre spécifié.

        :param str titre: Titre du chapitre.
        """
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, titre, 0, align='L')
        self.ln()

    def ajouter_image(self, chemin_image, x, y, taille):
        """
        Ajoute une image au PDF à l'emplacement spécifié.

        :param str chemin_image: Chemin de l'image à ajouter.
        :param float x: Position x de l'image.
        :param float y: Position y de l'image.
        :param float taille: Taille de l'image.
        """
        self.image(chemin_image, x=x, y=y, w=taille)

    def calcule_duree(self, h1, h2):
        """
        Calcule la durée entre deux horaires spécifiés.

        :param str h1: Horaire de départ au format 'aaaa/mm/jj hh:mm:ss'.
        :param str h2: Horaire d'arrivée au format 'aaaa/mm/jj hh:mm:ss'.
        :returns: Durée sous forme de chaîne de caractères.
        :rtype: Str
        """
        heure1 = float(h1[11:13]) + float(h1[14:16]) / 60
        heure2 = float(h2[11:13]) + float(h2[14:16]) / 60
        diff = heure2 - heure1
        diff_h = int(diff)
        diff_m = round((diff - int(diff)) * 60)
        return str(diff_h) + 'h' + str(diff_m) + 'min'

    def ajouter_tableau(self, donnees):
        """
        Ajoute un tableau au PDF. Formatage spécialement réalisé
        pour réceptionner les données d'émissions CO2 du programme.

        :param list donnees: Données à ajouter au tableau.
        """
        taille_max = 45

        # D'abord, on écrit les deux colonnes du tableau modèle_Engine et émission
        self.set_font('helvetica', 'B', 10)
        self.cell(taille_max, 7, "moteurs", 1, align='C')
        self.cell(taille_max, 7, "émission t(CO2)/pers", 1, align='C')
        self.set_font('helvetica', '', 10)
        self.ln()
        # Pour chaque modèle, on va afficher les émissions en fonction des moteurs
        for i in range(len(donnees[0])):
            self.cell(taille_max * 2, 7, str(donnees[0][i]), 1, align='C')
            self.set_font('helvetica', '', 10)
            self.ln()
            for j in range(len(donnees[1][i])):
                if i == 0 and j == 0:
                    self.set_text_color(0, 150, 0)
                    self.cell(taille_max, 7, str(donnees[1][i][j].split(' ')[0]), 1, align='C')
                    self.cell(taille_max, 7, str(donnees[2][i][j]), 1, align='C')
                    self.ln()
                    self.set_text_color(0, 0, 0)


                else:
                    self.cell(taille_max, 7, str(donnees[1][i][j].split(' ')[0]), 1, align='C')
                    self.cell(taille_max, 7, str(donnees[2][i][j]), 1, align='C')
                    self.ln()
        self.ln()

    def ajouter_separateur(self):
        """
        Ajoute un séparateur au PDF pour séparer les sections.
        Ajoute une ligne vide et une ligne de séparation.
        """
        self.ln(3)
        self.cell(0, 0, '', 'T')
        self.ln(2)

    def generer_pdf(self):
        """
        Génère le PDF avec toutes les sections et les informations du vol.

        Enregistre le PDF sous le nom 'Compte_rendu.pdf'.
        """
        # En-tête et pied de page personnalisés
        self.alias_nb_pages()
        self.set_auto_page_break(auto=True)

        # Titre principal
        self.set_font('helvetica', 'B', 16)
        self.cell(self.get_string_width('FICHE DE VOL :') + 2, 10, 'FICHE DE VOL :', 0)

        self.set_font('helvetica', '', 12)
        self.cell(0, 10, text=self.infos_vol[7] + ' ' + self.infos_vol[1], border=0)
        self.ln(7)

        self.set_font('helvetica', 'I', 12)
        self.cell(0, 10, self.infos_vol[5][0:10], 0, align='L')
        self.ln(10)

        # Section d'information
        long_page = self.w - 12.7 - 12.7

        # création d'une zone délimitée par plusieurs rectangles
        self.set_font('helvetica', '', 11)
        x_i = self.x
        y_i = self.y
        self.cell(long_page - self.get_string_width(self.infos_vol[9]) - 10, 10,
                  text=self.infos_vol[10] + ' (' + self.infos_vol[12] + ')', align='L')
        self.cell(self.get_string_width('Moteur'), h=10, text='Moteur :', align='L')
        self.ln(5)
        self.set_font('helvetica', 'B', 11)
        self.cell(self.get_string_width(self.infos_vol[3] + ' : '), 10, text=self.infos_vol[3] + ' : ')
        self.set_font('helvetica', '', 11)
        self.cell(long_page - self.get_string_width(self.infos_vol[9]) - self.get_string_width(
            self.infos_vol[3] + ' : ') - 10, 10, text=self.infos_vol[5][11:16])
        self.cell(self.get_string_width(self.infos_vol[9]), h=10, text=self.infos_vol[9], align='L')
        x_f = long_page + 12.7
        self.ln(5)
        self.set_font('helvetica', 'B', 11)
        self.cell(self.get_string_width(self.infos_vol[2] + ' : '), 10, text=self.infos_vol[2] + ' : ')
        self.set_font('helvetica', '', 11)
        self.cell(long_page - self.get_string_width(self.infos_vol[9]) - self.get_string_width(
            self.infos_vol[2] + ' : ') - 10, 10, text=self.infos_vol[6][11:16])
        self.cell(self.get_string_width(self.infos_vol[-3]), h=10, text=self.infos_vol[-3], align='L')
        self.ln(5)
        self.cell(long_page - self.get_string_width(self.infos_vol[9]) - 10, 10,
                  text='Distance parcourue : ' + str(round(float(self.infos_vol[-1]), 1)) + 'km')
        self.ln(5)
        self.cell(long_page - self.get_string_width(self.infos_vol[9]) - 10, 10,
                  text=f'Temps de vol : {self.calcule_duree(self.infos_vol[5], self.infos_vol[6])}')

        self.ln()
        y_f = self.y
        self.cell(self.get_string_width('icao24') + 3, 10, 'icao24', border=1)
        self.cell(0, 10, text=self.infos_vol[4], border=1, align='L')

        self.ln(10)
        self.rect(x_i, y_i, x_f - x_i, y_f - y_i)
        self.rect(x_i + long_page - self.get_string_width(self.infos_vol[9]) - 10, y_i,
                  x_f - x_i - (long_page - self.get_string_width(self.infos_vol[9]) - 10), y_f - y_i)

        self.ln(5)

        # Image mapView

        x_i = self.x
        y_i = self.y

        self.ajouter_image(self.map_chemin, 12.7 + long_page / 8, None, 3 * long_page / 4)
        y_f = self.y
        self.set_line_width(0.5)  # Épaisseur de trait de 2 points
        self.rect(x_i + long_page / 8, y_i, 3 * long_page / 4, y_f - y_i)
        self.set_line_width(0.2)  # Épaisseur de trait de 2 points

        # Séparateur
        self.ajouter_separateur()

        # Nouveau titre
        self.titre_chapitre(f'Emissions CO2 du vol en classe {self.classe} (en t par passager)')
        y_i = self.y

        # Image : Graphique
        self.ajouter_image(self.generer_graphique(), self.w-108, y_i, 105)

        self.ln(1)

        # Tableau
        donnees = self.infos_emission
        self.ajouter_tableau(donnees)

        self.set_line_width(1)  # Épaisseur de trait de 2 points
        self.rect(4, 4, self.w - 8, self.h - 8)

        # Enregistrer le PDF
        self.output("Compte_rendu.pdf")
