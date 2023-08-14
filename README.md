# Operational and tactical levers to reduce carbon emissions in temperature-sensitive freight transportation for pharmaceuticals
 
*(c) 2023 MIT Center for Transportation and Logistics - Jonas Lehmann, Dr. Matthias Winkenbach, Dr. Milena Janjevic*
## About

This tool is a demo implementation of the methodology presented in this [report](https://dspace.mit.edu/handle/1721.1/151744)
of the [MIT Center for Transportation and Logistics](https://ctl.mit.edu). It presents an estimation and allocation 
tool for carbon emissions for shipments in cold chain logistics. Shippers and providers of cooling containers may
use this tool to assess the carbon footprint of a shipment based on the fixed and variable emissions of the cooling
containers used as well as the transportation modes used by the carrier. We refer to the report for an explanation of the 
methodology and the underlying assumptions.

***

## Installation

Please note that this tool is a demo implementation of the methodology presented and was created for internal validation 
and analysis purposes only. There is no official support and it is not maintained.
Parts of the implementation are tailored to `Mac OS` (e.g. the Excel Macro) and may require further customization for non 
`Mac OS` users. 

The tool leverages the [NTMCalc Advanced 4.0](https://www.transportmeasures.org/ntmcalc/v4/basic/index.html#/) as primary source
for calculating carbon emissions from transportation activities. A valid [NTM membership](https://www.transportmeasures.org/en/membership/)
and corresponding `NTM API` credentials are needed to use this tool. Moreover, a valid `Goole Maps API` key is needed.  

Steps for setting up the tool:

1. Clone the repository and pull the `master` branch:
``````
git clone https://github.com/MIT-MLL/co2-estimator-cold-chain-logistics.git
``````
2. Install [anaconda](https://www.anaconda.com/). Create custom anaconda environment by opening the terminal and 
running the following command:
``````
conda create --name co2_estimation_tool
``````
Once activated, install the packages in `file requirements.txt`.



3. Insert API credentials of active NTMCalc Advanced 4.0 membership and Google Maps in `parameters/authentification_parameters.py`


Optional step for users wishing to use the Excel Macro and who use Mac:
4. Open `ExcelModels/automateCO2calculationPythonScript` in `Automator`. Enter the direct link to the anaconda environment 
and the Excel spreadsheet in the github repo like this (replace `my-user` with your user name):
``````
/Users/my-user/anaconda3/envs/co2_estimation_tool/bin/python /Users/my-user/GitHub/co2-estimator-cold-chain-logistics/main.py
``````

5. Open the Excel Workbook `ExcelModels/CO2 Emissions Calculator - 2023.xlsm`. 

* 5.1 Under the `Development` Tab, click `Macros` to edit the macro `RunCO2CalculationPythonScript`. Enter the link to 
the github folder to point the macro to the Automator Application.

* 5.2 Go to the sheet `Script Output Emissions Data`, via `Data` &rarr; `Get Data` &rarr; `Data Source Settings` to the
new path of the `transport_emissions_output.xlsx` file in the github folder.

Windows users may create a custom Macro calling `main.py` and link it to the `Calculate Emissions` button on the `Emissions Calculator` 
sheet in `CO2 Emissions Calculator - 2023.xlsm`

***


## Setup and usage

Once installation and setup is completed, relevant data about containers, networks, and shipments need to be inserted 
into `CO2 Emissions Calculator - 2023.xlsm`. Sheet `Description` provides an overview of the relevant sheets and the corresponding
data needed. The formatting of the individual sheets should not be changed to avoid errors by the Python script that reads in the data.

The main work sheet in the workbook is `Emissions Calculator`. It includes all relevant fields to calculate the emissions
of a shipment, such as data on the load (e.g. container type, weight, volume), itinerary components and specific section
on the aircraft components. Input fields are shaded in orange. Output fields are shaded in green.

The calculation of the shipment emissions are performed in four steps:
1. Insert shipment data as needed
2. Save workbook `(⌘ + S)`
3. Hit `Calculate Emission` button or run the `main.py` script from the terminal.
4. Refresh data (e.g., click `Refresh All` in `Data` section)

Note that calling the NTM API may take a few seconds. When running the macro via the `Calculate Emission` button, a turning 
wheel in the top right panel of the screen should appear, indicating that the script is running. The data can be refreshed once
the turning wheel has finished.


***

## Citation

Please cite via

```
@techreport{CTL2023CO2COLDCHAINS,
    title = {Operational and tactical levers to reduce carbon emissions in temperature-sensitive freight transportation for pharmaceuticals},
    year = {2023},
    author = {Lehmann, Jonas; Winkenbach, Matthias; Janjevic, Milena},
    institution = {MIT Center for Transportation and Logistics},
    url = {https://dspace.mit.edu/handle/1721.1/151744}}
```
