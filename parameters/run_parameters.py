#######################
######## PATHS ########
#######################

# Paths to excel spreadsheet
path_save_solution = './ExcelModels/Transportation_emissions_output.xlsx'

# set the path to the Excel Workbook
path_to_workbook = './ExcelModels/CO2 Emissions Calculator - 2023.xlsm'


############################
######## PARAMETERS ########
############################

# Additional parameters and specifications for the NTM Tool can be found here:
# https://www.transportmeasures.org/ntmcalc/apiexplorer/v1/support/NTMCalc_parameters1.0.html

# Queries can be explored and tested here:
# https://www.transportmeasures.org/ntmcalc/apiexplorer/v1/index.html?mode=basic

# Air freighter aircraft models
Air_freighters = ['Saab 340B', 'ATR 42-300 Freighter', 'AN-26 Freighter', 'F-27-500', 'BAe-146-200F',
                  'L-188 Electra Freighter', 'B737-300SF', 'A320 Freighter', 'AN-12', 'TU-204-100C',
                  'B727-200F', 'B757-200SF', 'A310-300 Freighter', 'B757-200F', 'B757-200PF', 'A300-B4 Freighter',
                  'B767-200ERF', 'IL-76MD', 'A300-600F', 'DC-8-63F', 'DC-8-73F', 'B767-300 Freighter', 'B767-300F',
                  'DC-10-30F', 'MD-11 Freighter', 'MD-11F', 'B777-200F', 'B747-200F', 'B747-400F', 'B747-800F']
# Belly cargo aircraft models
Belly_freighters = ['B737-700-Belly', 'A320 Belly', 'B737-800-Belly', 'B787-8-Belly', 'A330-300x-Belly',
                    'B767-200-Belly', 'B767-300-Belly', 'A330-300-Belly', 'A340-300-Belly', 'A330-200-Belly',
                    'B777-200-Belly', 'A340-600-Belly', 'B777-300-Belly', 'B747-400 Combi', 'B747-400-Belly',
                    'B777-300ER-Belly', 'A380-800-Belly']


# Default aircraft type used for provisioning calculations - adjust if needed
default_aircraft_type_ID = "B747-400F" # Freight aircraft
# default_aircraft_type_ID = "A330-200-Belly" # Belly freight - cargo

# the aircraft_type_ID is the default_aircraft_type_ID, but - are replaced with _, and everything is lower case
aircraft_type_ID = default_aircraft_type_ID.replace("-", "_").lower()

if default_aircraft_type_ID in Air_freighters:
    aircraft_type = "Freight aircraft"
elif default_aircraft_type_ID in Belly_freighters:
    aircraft_type = "Belly freight - cargo"
else:
    raise Exception("Please select a valid aircraft type")

# All values must be string
NTM_default_passenger_load_factor = "90" # in % - Attention: Can only be set to either `65` or `90` or may otherwise throw error. Default is 65%
volumetric_cargo_load_factor = "75"
cargo_load_factor_weight_air = "65"
commercial_volumetric_factor = "167"
VehicleType = "rigid_truck_7_5_t"
fuel = "diesel_b7_eu"
road_type = "average_road"
euro_class = "euro_6"
cargo_carrier_capacity_weight = "6.0"
type_of_waters = "ocean"
ship_size = "40000"
cargo_load_factor_weight_maritime = "70"

NTM_default_parameters = {
    'Air':{"aircraft_type_ID":aircraft_type_ID,
           'aircraft type':aircraft_type,
           "volumetric_cargo_load_factor":volumetric_cargo_load_factor,
           "cargo_load_factor_weight":cargo_load_factor_weight_air,
           "commercial_volumetric_factor":commercial_volumetric_factor,
           "passenger_load_factor":NTM_default_passenger_load_factor},
    'Road':{"VehicleType":VehicleType,
            "fuel":fuel,
            "road_type": road_type,
            "euro_class": euro_class,
            "cargo_carrier_capacity_weight":cargo_carrier_capacity_weight},
    'Maritime':{"type_of_waters":type_of_waters,
                "ship_size":ship_size,
                "cargo_load_factor_weight":cargo_load_factor_weight_maritime},
}

default_belly_freighter = 'B777-300ER-Belly'


####################################
######## ADDITIONAL FACTORS ########
####################################

# Radiative Forcing Index (RFI)
RFI = 2

# Flight detour we apply to account for maneuvering the aircraft. 95km from EN 16258 standard is used
DETOUR_KM = 95
