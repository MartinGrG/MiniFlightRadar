"""
Ce script permet d'établir les fonctions nécessaires au calcul de l'empreinte carbone globale d'un vol et de
l'équivalent pour un passager.
"""

CO2_factors = [
    {"Type": "Standard court-courrier",
     "S": 157.86,  # Nombre moyen de sièges
     "PLF": 0.796,  # Facteur de charge des passagers
     "DC": 95,  # Correction de détour
     "CF": 0.26,  # Facteur de fret
     "CW": [1, 1, 1.5, 1.5],  # Classe économique, Premium Economy, Affaires, 1ère
     "FE": 3.16,  # Facteur d’émission
     "P": 0.538,  # Pré-production
     "M": 3,  # Multiplicateur
     "AF": 0.00034,  # Facteur de l’aéronef
     "A": 11.68,  # Aéroport/infrastructure
     "a": 0.000007,
     "b": 2.775,
     "c": 1260.608},

    {"Type": "B737",
     "S": 148.00,
     "PLF": 0.796,
     "DC": 95,
     "CF": 0.23,
     "CW": [1, 1, 1.5, 1.5],
     "FE": 3.16,
     "P": 0.538,
     "M": 3,
     "AF": 0.00034,
     "A": 11.68,
     "a": 0.00016,
     "b": 1.454,
     "c": 1531.722},

    {"Type": "A320",
     "S": 165.00,
     "PLF": 0.796,
     "DC": 95,
     "CF": 0.26,
     "CW": [1, 1, 1.5, 1.5],
     "FE": 3.16,
     "P": 0.538,
     "M": 3,
     "AF": 0.00034,
     "A": 11.68,
     "a": 0.000032,
     "b": 2.588,
     "c": 1212.084},

    {"Type": "Standard long-courrier ",
     "S": 302.58,
     "PLF": 0.82,
     "DC": 95,
     "CF": 0.26,
     "CW": [1, 1.5, 4, 5],
     "FE": 3.16,
     "P": 0.538,
     "M": 3,
     "AF": 0.00034,
     "A": 11.68,
     "a": 0.00029,
     "b": 3.475,
     "c": 3259.691},

    {"Type": "B777",
     "Nombre moyen de sièges (S)": 370,
     "PLF": 0.82,
     "DC": 95,
     "CF": 0.45,
     "CW": [1, 1.5, 4, 5],
     "FE": 3.16,
     "P": 0.538,
     "M": 3,
     "AF": 0.00034,
     "A": 11.68,
     "a": 0.00034,
     "b": 6.112,
     "c": 3403.041},

    {"Type": "A330",
     "S": 287,
     "PLF": 0.82,
     "DC": 95,
     "CF": 0.06,
     "CW": [1, 1.5, 4, 5],
     "FE": 3.16,
     "P": 0.538,
     "M": 3,
     "AF": 0.00034,
     "A": 11.68,
     "a": 0.00034,
     "b": 4.384,
     "c": 2457.737}]
