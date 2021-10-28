AUTHOR: Edit Lelkes

DESCRIPTION
This program processes csv flight data and searches flights (direct or layover) and sorts them in ascending order
based on total travel price.

ARGUMENTS
There are 3 positional arguments which are mandatory:
1. the path to csv file
    The csv file should have columns named:
    flight_no,origin,destination,departure,arrival,base_price,bag_price,bags_allowed
2. origin airport IATA
3. destination airport IATA

There are 3 additional optional arguments:
  -h, --help            show the help message and exit
  --bags                Number of bags to travel with, default is 0
  --return_flight       When this argument added, the program searches for returning flights
  --output_mode         Determines the form of output. There are 2 options: 'stdout' and 'output_files'.
                        'stdout' - prints the found flights in json format to standard output. This is the default value
                        'output_files' - creates a .json file with the found flights (when the program searches
                        for return flights too, it creates 2 files).

USAGE:
python -m main example1.csv DHE SML
    Loads the flights from example1.csv and then searches flights from DHE airport to SML airport.
    Since the --bags argument was not specified no bags need to be allowed on the flights
    Since the --return_flight argument was not specified no search for return flights will be performed.
    The output is printed to the standard output because --output_mode was not specified (default is stdout).

python -m main example1.csv NRX SML --bags=2 --return_flight --output_mode=output_files
    Loads the flights from example1.csv.
    After that searches flights from NRX airport to SML airport with minimum of 2 bags allowed.
    It also searches for returning flights because --return_flight was specified.
    The output is generated to 2 separate json files: flights.json and return_flights.json.


EXAMPLE OUTPUT:
see: example_output_flights.json






