"""
Ce script permet d'établir les fonctions nécessaires au calcul de l'empreinte carbone globale d'un vol et de
l'équivalent pour un passager.
"""

from DataBase import engine_emission, aircraft_emission, model_is_present

EF = 3.16  # Facteur d’émission
P = 0.538  # Facteur de pré-production
M = 3  # Multiplicateur
AF = 0.00034  # Facteur de l’aéronef
A = 11.68  # Facteaur d'aéroport/infrastructure

# Classe économique, Premium Economy, Affaires, 1ère
SEAT_CLASS = {
    "economy": 0,
    "premium economy": 1,
    "affaires": 2,
    "première": 3
}


def global_carbon_emissions(duration, uid, engines_nb=1):
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

    engine_info = engine_emission(uid).reset_index(drop=True)

    # Calcule les émissions de carbone globales en utilisant les facteurs et la formule quadratique
    return ((engine_info["Fuel Flow T/O (kg/sec)"]*0.3*duration+engine_info["Fuel LTO Cycle (kg)  "][0])*engines_nb
            * (P+EF*M))


def passenger_carbon_emissions(distance, duration, model, uid, engines_nb=1, seat_class="economy"):
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
    if model_is_present(model):
        # Si le modèle n'est pas trouvé, détermine si le vol est court-courrier ou long-courrier
        if distance < 2000:
            model = "Standard court-courrier"  # Modèle pour vol court-courrier
        else:
            model = "Standard long-courrier"  # Modèle pour vol long-courrier

    # Récupère les facteurs de CO2 pour le modèle déterminé
    aircraft_info = aircraft_emission(model)

    # Calcule les émissions de CO2 par passager en tenant compte de la classe de siège
    return (global_carbon_emissions(duration, uid, engines_nb)*(1-aircraft_info["CF"]) *
            aircraft_info["CW"][SEAT_CLASS[seat_class]]/(aircraft_info["S"]*aircraft_info["PLF"])+AF*distance+A)
