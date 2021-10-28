from typing import List, Dict, Union
import argparse
import json
from flight_manager import FlightManager

if __name__ == "__main__":

    def generate_output(output_mode: str, data: List[Dict[str, Union[List, int, str, float]]], filename: str) -> None:
        """
        Function for generating output based on command line argument --output_mode.

        :param output_mode: Output mode: either 'stdout' or 'output_files'.
        :param data: Formatted search results.
        :param filename: Name of the output file.
        """
        json_data = json.dumps(data, indent=2)
        if output_mode == 'stdout':
            print(json_data)
        elif output_mode == 'output_files':
            with open(filename, 'w') as f:
                f.write(json_data)


    """
    Processing command line arguments with argparse
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_filepath', type=str, help='Path to csv file')
    parser.add_argument('origin', type=str, help='Airport IATA - origin')
    parser.add_argument('destination', type=str, help='Airport IATA - destination')
    parser.add_argument('--bags', type=int, default=0, help='Number of bags for the trip')
    parser.add_argument('--return_flight', action='store_true',
                        help='When return argument added, the program searches for returning flights')
    parser.add_argument('--output_mode', default='stdout', choices=['stdout', 'output_files'],
                        help='Specifies whether the output is printed on command line or generated to file')
    arguments = parser.parse_args()

    """
    Initialization of FlightManager and search of connections.
    """
    manager = FlightManager(arguments.csv_filepath)

    # Checking the airport codes given by the user
    if arguments.origin.upper() not in manager.airports:
        raise RuntimeError('Code for origin airport ' + arguments.origin + ' is not in dataset.')
    if arguments.destination.upper() not in manager.airports:
        raise RuntimeError('Code for destination airport ' + arguments.destination + ' is not in dataset.')
    if arguments.origin.upper() == arguments.destination.upper():
        raise RuntimeError('The origin and the destination airports are identical.')

    origin_airport = manager.airports[arguments.origin.upper()]
    destination_airport = manager.airports[arguments.destination.upper()]

    flights = manager.search_flights(origin_airport, destination_airport, arguments.bags)
    generate_output(arguments.output_mode, flights, 'flights.json')

    if arguments.return_flight:
        return_flights = manager.search_flights(destination_airport, origin_airport, arguments.bags)
        generate_output(arguments.output_mode, return_flights, 'return_flights.json')
