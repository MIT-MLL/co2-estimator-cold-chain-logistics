# import packages
from haversine import haversine
import searoute as sr
import pandas as pd
import numpy as np
import googlemaps
import requests
import copy

from parameters import run_parameters
from objects.NTM_Authentifier import Auth
from parameters.authenfitication_parameters import NTM_authentification_settings, API_KEY

class EmissionsCalculator:
    """
    Class object calculating the emissions from transportation and repositioning/provisioning
    """

    def __init__(self):
        self.auth = Auth(NTM_authentification_settings)
        self.gmaps = googlemaps.Client(key=API_KEY)


    def calculate_shipment_transportation_emissions(self):
        """
        Calculates the transportation emissions for the new shipment
        """

        # get the transportation data
        transportation_df = pd.read_excel(run_parameters.path_to_workbook, sheet_name='Script input transpo data')

        airfreight_emissions = 0
        road_freight_emissions = 0

        # Calculate the emissions for each leg
        for index, row in transportation_df.iterrows():

            # retrieve the shipment data
            shipment_weight_kg = row['Shipment Weight [kg]']
            shipment_volume_m3 = row['Shipment Volume [m3]']

            # get the origin and destination points
            origin_latlong = (row['Origin Latitude'], row['Origin Longitude'])
            dest_latlong = (row['Destination Latitude'], row['Destination Longitude'])

            # calculate road freight emissions
            if row['Transportation Mode']=='Road':
                road_freight_emissions+=self.calculate_road_freight_emissions(shipment_weight_kg, shipment_volume_m3,
                                                                 origin_latlong, dest_latlong, self.transport_dict['new shipment'])

            # calculate airfreight emissions
            elif row['Transportation Mode']=='Air':
                airfreight_emissions+=self.calculate_air_freight_emissions(shipment_weight_kg, shipment_volume_m3,
                                                               origin_latlong, dest_latlong, self.transport_dict['new shipment'])


        return airfreight_emissions, road_freight_emissions



    def calculate_air_freight_emissions(self,shipment_weight_kg, shipment_volume_m3, origin_latlong, destination_latlong,
                                        parameter_dict, distance_km=None):
        """
        Calculates the emissions from air freight transportation
        :param shipment_weight_kg: the weight of the shipment
        :param shipment_volume_m3: the volume of the shipment
        :param origin_latlong: the origin_latlong as lat long pair
        :param destination_latlong: the destination as lat long pair
        :return: the emissions
        """

        if distance_km==None:
            # set haversine distance
            distance_km = np.around(haversine(origin_latlong, destination_latlong) +
                                    run_parameters.DETOUR_KM, 2)

        try:
            # get the access token
            access_token = self.auth.get_access_token()

            # set default aircraft type
            aircraft_type = "freight_aircraft"

            API_parameters = [
                                        {
                                            "id": "calculation_model",
                                            "value": "shipment_transport_volumetric_weight"
                                        },
                                        {
                                            "id": "aircraft_type",
                                            "value": str(parameter_dict['NTM parameters']['Air']['aircraft_type_ID'])
                                        },
                                        {
                                            "id": "shipment_volume",
                                            "value": str(np.around(shipment_volume_m3,2)),
                                            "unit": "m3"
                                        },
                                        {
                                            "id": "shipment_weight",
                                            "value": str(np.around(shipment_weight_kg,2)),
                                            "unit": "kg"
                                        },
                                        {
                                            "id": "distance",
                                            "value": str(np.around(distance_km,2)),
                                            "unit": "km"
                                        },
                                        {
                                            "id": "volumetric_cargo_load_factor",
                                            "value": str(parameter_dict['NTM parameters']['Air']['volumetric_cargo_load_factor']),
                                            "unit": "%weight"
                                        },
                                        {
                                            "id": "cargo_load_factor_weight",
                                            "value": str(parameter_dict['NTM parameters']['Air']['cargo_load_factor_weight']),
                                            "unit": "%weight"
                                        },
                                        {
                                            "id": "commercial_volumetric_factor",
                                            "value": str(parameter_dict['NTM parameters']['Air']['commercial_volumetric_factor']),
                                            "unit": "kg/m3"
                                        }]

            # add passenger load factor parameter if needed:
            if parameter_dict['NTM parameters']['Air']['aircraft type'] =='Belly freight - cargo':
                API_parameters.append({"id": "passenger_load_factor",
                                   "value": str(parameter_dict['NTM parameters']['Air']['passenger_load_factor'])})

                aircraft_type = "belly_freighter_cargo"

            # run the request
            res = requests.post('https://api.transportmeasures.org/v1/transportactivities',
                                headers={'Content-Type': 'application/json',
                                         'Authorization': 'Bearer ' + access_token},
                                json={
                                    "calculationObject":
                                        {
                                            "id": aircraft_type,
                                            "version": "1"
                                        },
                                    "parameters": API_parameters})

            # run the query and get the response
            response = res.json()

        except Exception as err:
            print(err)
            return False

        # return the CO2 emissions
        co2_emissions_kg = run_parameters.RFI*np.around(response['resultTable']['totals'][response['resultTable']['index']['co2_total']]['value'], 2)

        return co2_emissions_kg

    def calculate_road_freight_emissions(self,shipment_weight_kg, shipment_volume_m3, origin_latlong, destination_latlong,
                                         parameter_dict, distance_km=None):
        """
        Calculates the emissions from road freight transportation
        :param shipment_weight_kg: the weight of the shipment
        :param shipment_volume_m3: the volume of the shipment
        :param origin_latlong: the origin_latlong as lat long pair
        :param destination: the destination as lat long pair
        :return: the emissions
        """

        if distance_km==None:

            # query distance via google maps API
            results = self.gmaps.distance_matrix(origin_latlong, destination_latlong,
                                                 mode='driving',
                                                 departure_time='now',
                                                 traffic_model='best_guess')

            # get the distance in km
            distance_km = np.around(results['rows'][0]['elements'][0]['distance']['value'] / 1000, 2)

            # if distance is 0, set to value close to 0 to avoid crash in emissions transportation calculation
            if distance_km==0:
                distance_km=0.01

        # get the weight in tons
        shipment_weight_ton = shipment_weight_kg / 1000

        # get the tonne-kilometres
        shipment_tkms = np.around(distance_km * shipment_weight_ton, 2)

        try:
            # Get the access token needed for authentication and authorization in the web service
            access_token = self.auth.get_access_token()

            # run the query
            res = requests.post('https://api.transportmeasures.org/v1/transportactivities',
                                headers={'Content-Type': 'application/json',
                                         'Authorization': 'Bearer ' + access_token},
                                json={"calculationObject":
                                          {"id": "rigid_truck_7_5_t",
                                           "version": "1"},
                                      "parameters": [
                                          {
                                              "id": "calculation_model",
                                              "value": "shipment_transport_tonne_kilometres"
                                          },
                                          {
                                              "id": "fuel",
                                              "value": str(parameter_dict['NTM parameters']['Road']['fuel'])
                                          },
                                          {
                                              "id": "road_type",
                                              "value": str(parameter_dict['NTM parameters']['Road']['road_type'])
                                          },
                                          {
                                              "id": "euro_class",
                                              "value": str(parameter_dict['NTM parameters']['Road']['euro_class'])
                                          },
                                          {
                                              "id": "transport_effort",
                                              "value": str(shipment_tkms),
                                              "unit": "tkm"
                                              },
                                          {
                                              "id": "cargo_carrier_capacity_weight",
                                              "value": str(parameter_dict['NTM parameters']['Road']['cargo_carrier_capacity_weight']),
                                              "unit": "tonne"
                                              }
                                          ]})

            # get the json response
            response = res.json()

        except Exception as err:
            print(err)
            return False

        # get the emissions
        emissions_kg = np.around(response['resultTable']['totals'][response['resultTable']['index']['co2_total']]['value'], 2)

        return emissions_kg


    def calculate_maritime_freight_emissions(self, shipment_weight_kg, shipment_volume_m3,
                                             origin_latlong, destination_latlong,
                                             parameter_dict, distance_km=None):
        """
        Calculates the emissions from road freight transportation
        :param shipment_weight_kg: the weight of the shipment
        :param shipment_volume_m3: the volume of the shipment
        :param origin_latlong: the origin_latlong as lat long pair
        :param destination: the destination as lat long pair
        :return: the emissions
        """

        if distance_km==None:
            origin_longlat = origin_latlong[::-1]
            destination_longlat = destination_latlong[::-1]

            origin_longlat = list(origin_longlat)
            destination_longlat = list(destination_longlat)

            distance_km = sr.searoute(origin_longlat, destination_longlat, units="km")['properties']['length']

        try:
            # Get the access token needed for authentication and authorization in the web service
            access_token = self.auth.get_access_token()

            # get the weight in tons
            shipment_weight_ton = shipment_weight_kg / 1000

            # run the query
            res = requests.post('https://api.transportmeasures.org/v1/transportactivities',
                                headers={'Content-Type': 'application/json',
                                         'Authorization': 'Bearer ' + access_token},
                                json={"calculationObject":
                                    {"id": "container_ship",
                                    "version": "1"},
                                      "parameters": [
                                          {
                                          "id": "calculation_model",
                                          "value": "shipment_transport_weight"
                                          },
                                          {
                                              "id": "type_of_waters",
                                              "value": parameter_dict['NTM parameters']['Maritime']['type_of_waters']
                                          },
                                          {
                                              "id": "ship_size",
                                              "value": parameter_dict['NTM parameters']['Maritime']['ship_size'],
                                              "unit": "dwt"
                                          },
                                          {
                                              "id": "shipment_weight",
                                              "value": str(shipment_weight_ton),
                                              "unit": "tonne"
                                          },
                                          {
                                              "id": "distance",
                                              "value": str(distance_km),
                                              "unit": "km"
                                          },
                                          {
                                              "id": "cargo_load_factor_weight",
                                              "value": parameter_dict['NTM parameters']['Maritime']['cargo_load_factor_weight'],
                                              "unit": "%weight"
                                          }
                                      ]})
            # get the json response
            response = res.json()

        except Exception as err:
            print(err)
            return False

        # get the emissions
        emissions_kg = np.around(response['resultTable']['totals'][response['resultTable']['index']['co2_total']]['value'], 2)

        return emissions_kg



    def calculate_repositioning_emissions(self):
        """
        Calculate the emissions from repositioning/provisioning
        :return: the emissions created by repositioning/provisioning and attributed to the new shipment
        """

        # read in the csv
        df = pd.read_excel(run_parameters.path_to_workbook, sheet_name='Script input provisioning data')

        # only take the subset of repositioning data that matches the container type
        df = df[df['Container Type'] == self.transport_dict['new shipment']['shipment parameters']['Container Type']]

        # calculate the total number of outgoing shipments
        number_of_outgoing_shipments = sum(df[df['Origin'] == self.transport_dict['new shipment']['shipment parameters']['Origin Service Center']]['Number of containers shipped'])+\
                                       self.transport_dict['new shipment']['shipment parameters']['Number of containers shipped']

        # take the subset of repositioning shipments with the same destination as our origin service center
        df_repositioning = df[(df['Destination Service Center'] ==
                               self.transport_dict['new shipment']['shipment parameters']['Origin Service Center']) &
                              (df['Shipment Type'] == 'Provisioning')]

        # get nominal weight and volume for containers
        weight_per_empty_container = self.transport_dict['new shipment']['shipment parameters']['Empty Container Weight [kg]']/\
                                     self.transport_dict['new shipment']['shipment parameters']['Number of containers shipped']
        outer_volume_per_container = self.transport_dict['new shipment']['shipment parameters']['Shipment Volume [m3]']/\
                                     self.transport_dict['new shipment']['shipment parameters']['Number of containers shipped']

        # calculate the emissions from repositioning shipments
        repositioning_emissions=0
        for index, row in df_repositioning.iterrows():

            # retrieve the shipment data
            shipment_weight_kg = row['Number of containers shipped']*weight_per_empty_container
            shipment_volume_m3 = row['Number of containers shipped'] * outer_volume_per_container

            # get the origin and destination points
            origin_latlong = (row['Origin Latitude'], row['Origin Longitude'])
            dest_latlong = (row['Destination Latitude'], row['Destination Longitude'])

            distance_km=None
            if row['Distance [km] (if available)']>0:
                distance_km=row['Distance [km] (if available)']

            # calculate road freight emissions
            if row['Transportation Mode']=='Road':
                repositioning_emissions+=self.calculate_road_freight_emissions(shipment_weight_kg, shipment_volume_m3,
                                                                 origin_latlong, dest_latlong, self.transport_dict['repositioning'],
                                                                               distance_km=distance_km)

            # calculate airfreight emissions
            elif row['Transportation Mode']=='Air':
                repositioning_emissions+=self.calculate_air_freight_emissions(shipment_weight_kg, shipment_volume_m3,
                                                               origin_latlong, dest_latlong, self.transport_dict['repositioning'],
                                                                              distance_km=distance_km)

            elif row['Transportation Mode']=='Maritime':
                repositioning_emissions += self.calculate_maritime_freight_emissions(shipment_weight_kg, shipment_volume_m3,
                                                                                     origin_latlong, dest_latlong,
                                                                                     self.transport_dict['repositioning'],
                                                                                     distance_km=distance_km)


        # compute repositioning emissions per container shipment
        repositioning_emissions_per_outgoing_container = repositioning_emissions/number_of_outgoing_shipments

        # total attributable repositioning emissions for the new shipment
        repositioning_emissions_for_new_shipment = repositioning_emissions_per_outgoing_container*\
                                                   self.transport_dict['new shipment']['shipment parameters']['Number of containers shipped']

        return repositioning_emissions_for_new_shipment



    def create_transportation_dict(self):
        """
        Reads in the workbook and calculates the necessary parameters and routes. Stores it in self
        """

        # set dictionary
        transport_dict = dict()

        # Create parameters for new shipment emissions
        transport_dict['new shipment'] = self.create_newshipment_parameters()

        # Create parameters for repositioning emissions
        transport_dict['repositioning'] = self.create_repositioning_parameters()

        self.transport_dict = transport_dict


    def create_newshipment_parameters(self):
        """
        Creates the parameters for the new shipment
        """

        # set the default parameters for NTM parameters
        dic = dict()
        dic['NTM parameters'] = copy.deepcopy(run_parameters.NTM_default_parameters)

        # read in the relevant sheet & create the parameter dict
        df = pd.read_excel(run_parameters.path_to_workbook, sheet_name='Script input new shipment data')

        # create the parameter dict
        a = list(df.columns)
        b = list(df.loc[0].values)
        shipment_dict = dict(zip(a, b))

        # set the shipment parameters
        dic['shipment parameters'] = shipment_dict

        # update the air freight shipment data
        shipment_airplane_model = dic['shipment parameters']['Aircraft Model']
        if (shipment_airplane_model == 'Not available') & (dic['shipment parameters']['Aircraft Type']=='Belly freight - cargo'):
            dic['NTM parameters']['Air']["aircraft_type_ID"]= run_parameters.default_belly_freighter.lower().replace('-', '_').replace(' ', '_')
        elif shipment_airplane_model != 'Not available':
            dic['NTM parameters']['Air']["aircraft_type_ID"]=dic['shipment parameters']['Aircraft Model'].lower().replace('-', '_').replace(' ', '_')
        dic['NTM parameters']['Air']["aircraft model"] = shipment_airplane_model
        dic['NTM parameters']['Air']["aircraft type"] = dic['shipment parameters']['Aircraft Type']
        dic['NTM parameters']['Air']["volumetric_cargo_load_factor"] = str(dic['shipment parameters']['Volumetric Load Factor [%]'])
        dic['NTM parameters']['Air']["cargo_load_factor_weight"] = str(dic['shipment parameters']['Weight Load Factor [%]'])

        return dic

    def create_repositioning_parameters(self):
        """
        Creates the parameters for the new shipment
        """

        # set the default parameters for NTM parameters
        dic = dict()
        dic['NTM parameters'] = copy.deepcopy(run_parameters.NTM_default_parameters)

        return dic