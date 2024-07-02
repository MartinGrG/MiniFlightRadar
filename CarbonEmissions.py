"""
Ce script permet d'établir les fonctions nécessaires au calcul de l'empreinte carbone globale d'un vol et de
l'équivalent pour un passager.
"""

from DataBase import emission

CO2_factors = {
    "Standard court-courrier":
    {"S": 157.86,  # Nombre moyen de sièges
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
    "737":
    {"S": 148.00,
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
    "A320":
    {"S": 165.00,
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
    "Standard long-courrier":
    {"S": 302.58,
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
    "B777":
    {"Nombre moyen de sièges (S)": 370,
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
    "A330":
    {"S": 287,
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
     "c": 2457.737}}


SEAT_CLASS = {
    "economy": 0,
    "premium economy": 1,
    "affaires": 2,
    "première": 3
}


def global_carbon_emissions(gcd, duration, model, uid, engines_nb=1):
    """
    Calcule les émissions globales de CO2 pour un vol donné.

    Cette fonction utilise les données de distance de vol et le modèle d'avion pour
    estimer les émissions de CO2 en utilisant une formule quadratique basée sur plusieurs
    facteurs spécifiques au modèle d'avion.

    Arguments :
    gcd (float) : La distance géodésique (great circle distance) en kilomètres.
    model (str) : Le modèle de l'avion. Si le modèle n'est pas reconnu, un modèle par défaut
                  est sélectionné en fonction de la distance (court-courrier ou long-courrier).

    Retour :
    float : Les émissions estimées de CO2 en kilogrammes pour le vol spécifié.
    """

    engine_info = emission(uid).reset_index()

    # Vérifie si le modèle donné est dans le dictionnaire des facteurs de CO2 (CO2_factors)
    if model not in CO2_factors:
        # Si le modèle n'est pas trouvé, détermine si le vol est court-courrier ou long-courrier
        if gcd < 2000:
            model = "Standard court-courrier"  # Modèle pour vol court-courrier
        else:
            model = "Standard long-courrier"  # Modèle pour vol long-courrier

    # Récupère les facteurs de CO2 pour le modèle déterminé
    factors = CO2_factors[model]

    # Calcule les émissions de carbone globales en utilisant les facteurs et la formule quadratique
    return ((engine_info["Fuel Flow T/O (kg/sec)"]*0.3*duration+engine_info["Fuel LTO Cycle (kg)  "][0])*engines_nb
            * (factors["P"]+factors["FE"]*factors["M"]))


def passenger_carbon_emissions(gcd, duration, model, uid, engines_nb=1, seat_class="economy"):
    """
    Calcule les émissions de CO2 par passager en fonction de la distance, du modèle d'avion et de la classe de siège.

    Parameters:
    gcd (int): Distance en kilomètres.
    model (str): Modèle de l'avion.
    seat_class (str): Classe de siège du passager (par défaut : "economy").

    Returns:
    float: Emissions de CO2 par passager.
    """
    # Vérifie si le modèle donné est dans le dictionnaire des facteurs de CO2 (CO2_factors)
    if model not in CO2_factors:
        # Si le modèle n'est pas trouvé, détermine si le vol est court-courrier ou long-courrier
        if gcd < 2000:
            model = "Standard court-courrier"  # Modèle pour vol court-courrier
        else:
            model = "Standard long-courrier"  # Modèle pour vol long-courrier

    # Récupère les facteurs de CO2 pour le modèle déterminé
    factors = CO2_factors[model]

    # Calcule la distance corrigée en ajoutant la correction de détour (DC)
    distance = gcd+factors["DC"]

    # Calcule les émissions de CO2 par passager en tenant compte de la classe de siège
    return (global_carbon_emissions(gcd, duration, model, uid, engines_nb)*(1-factors["CF"]) *
            factors["CW"][SEAT_CLASS[seat_class]]/(factors["S"]*factors["PLF"])+factors["AF"]*distance+factors["A"])
