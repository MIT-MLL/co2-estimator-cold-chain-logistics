# import packages
import numpy as np
import pandas as pd
from parameters.run_parameters import path_save_solution
from objects.EmissionsCalculator import EmissionsCalculator as EMC

if __name__ == "__main__":

    # create emissions calculator object
    emc = EMC()

    # create dictionary with all parameters as well as transportation routes
    emc.create_transportation_dict()

    # Calculate transportation emissions
    airfreight_emissions_kg, road_freight_emissions_kg = emc.calculate_shipment_transportation_emissions()

    # Calculate repositioning emissions
    repositioning_emissions_kg = emc.calculate_repositioning_emissions()

    # save them temporarily as df
    emissions_dict = {'Variable road freight emissions': np.around(road_freight_emissions_kg, 2),
                      'Variable air freight emissions': np.around(airfreight_emissions_kg, 2),
                      'Repositioning/Provisioning emissions': np.around(repositioning_emissions_kg, 2)}
    new_sheet = pd.DataFrame(emissions_dict, index=[0])

    # save it as Excel sheet
    new_sheet.to_excel(path_save_solution)

    print('Finished.')