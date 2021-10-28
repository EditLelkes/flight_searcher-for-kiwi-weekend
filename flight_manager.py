import csv
from typing import List, Dict, Union
import datetime


class Flight:
    """
    Objects of the Flight class are flights with their properties.
    """
    def __init__(self, flight_no: str, origin: "Airport", destination: "Airport", departure: str, arrival: str,
                 base_price: str, bag_price: str, bags_allowed: str):
        """
        Constructor.

        :param flight_no: Flight number.
        :param origin: Departure airport.
        :param destination: Arrival airport.
        :param departure: Departure time.
        :param arrival: Arrival time.
        :param base_price: Price of ticket without bags.
        :param bag_price: Price for 1 bag.
        :param bags_allowed: Number of bags allowed.
        """
        self.flight_no = flight_no
        self.origin = origin
        self.destination = destination
        self.departure = departure
        self.arrival = arrival
        self.departure_datetime_format = datetime.datetime.strptime(departure, "%Y-%m-%dT%H:%M:%S")
        self.arrival_datetime_format = datetime.datetime.strptime(arrival, "%Y-%m-%dT%H:%M:%S")
        self.base_price = float(base_price)
        self.bag_price = int(bag_price)
        self.bags_allowed = int(bags_allowed)


class Airport:
    """
    Objects of the Airport class are airports containing departure flights.
    """
    def __init__(self, name: str):
        """
        Constructor.

        :param name: Airport IATA.
        """
        self.name = name
        self.departure_flights: List[Flight] = []


class FlightManager:
    """
    This class processes the cvs file of flight information, creates instances of Flight and Airport classes
    and performs flight searches and formatting of the results.
    """
    def __init__(self, csv_file: str):
        """
        Constructor.
        Processes the csv file and from the csv data creates a dictionary of Airports where the key is the airport IATA.

        :param csv_file: Path to csv file containing flight information.
        """
        self.airports: Dict[str, Airport] = {}
        with open(csv_file, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['origin'] not in self.airports:
                    self.airports[row['origin']] = Airport(row['origin'])
                if row['destination'] not in self.airports:
                    self.airports[row['destination']] = Airport(row['destination'])

                new_flight = Flight(row['flight_no'], self.airports[row['origin']], self.airports[row['destination']],
                                    row['departure'], row['arrival'], row['base_price'], row['bag_price'],
                                    row['bags_allowed'])

                new_flight.origin.departure_flights.append(new_flight)

    @staticmethod
    def _check_flight_criteria(bags, flight: Flight, connections: List[Flight]) -> bool:
        """
        Checks whether it is allowed to bring the specified number of bags to a given Flight.
        Then checks whether the layover time is between 1 an 6 hours.
        Checks whether the flight is not returning to an already visited airport.
        If every condition fits, returns True.

        :param bags: Number of bags the traveller wants to bring to the flight.
        :param flight: Flight to check.
        :param connections: List of flights already travelled on.
        :return: Returns True if the flight meets all the criteria, else returns False.
        """
        if flight.bags_allowed < bags:
            return False
        if len(connections) > 0:
            layover_time = flight.departure_datetime_format - connections[-1].arrival_datetime_format
            layover_time = float(layover_time.total_seconds() / 3600)
            if layover_time < 1 or layover_time > 6:
                return False
        if any(connection.origin == flight.destination for connection in connections):
            return False
        return True

    def _flight_search_calc(self, start: Airport, finish: Airport, nr_bags: int,
                            connections: List[Flight]) -> List[List[Flight]]:
        """
        Searches for all possible connections between the specified start and finish airports recursively.
        Each connecting flight on the list must meet the criteria checked by '_check_flight_criteria()'.

        :param start: Origin airport.
        :param finish: Destination airport.
        :param nr_bags: Number of bags specified by user.
        :param connections: List of flights already used in the current trip,
                            necessary to filter out already visited airports
        :return: List of every possible connections (list of flights) between the origin and the destination airport.
        """
        found_flights: List[List[Flight]] = []
        for flight in start.departure_flights:
            if self._check_flight_criteria(nr_bags, flight, connections):
                new_connections = connections + [flight]
                if flight.destination.name == finish.name:
                    found_flights.append(new_connections)
                else:
                    new_found_flights = self._flight_search_calc(flight.destination, finish, nr_bags, new_connections)
                    found_flights.extend(new_found_flights)

        return found_flights

    @staticmethod
    def _format_flights_to_list(connection: List[Flight]) -> List[Dict]:
        """
        Converts the specified connection (list of subsequent flights) to a list of dictionaries
        where one dictionary contains information about one specific flight.

        :param connection: List of subsequent flights for travelling between two airports.
        :return: List of dictionaries containing flight information.
        """
        formatted_flight_list = []
        for flight in connection:
            flight_dict = {
                'flight_no': flight.flight_no,
                'origin': flight.origin.name,
                'destination': flight.destination.name,
                'departure': flight.departure,
                'arrival': flight.arrival,
                'base_price': flight.base_price,
                'bag_price': flight.bag_price,
                'bags_allowed': flight.bags_allowed
            }
            formatted_flight_list.append(flight_dict)
        return formatted_flight_list

    @staticmethod
    def _total_price_calc(connection: List[Flight], bags_count: int) -> float:
        """
        Calculates the total price of the specified flight connection including the bag prices.

        :param connection: List of subsequent flights.
        :param bags_count: Number of bags specified by the user.
        :return: Total price for the whole connection.
        """
        total_price = 0
        for flight in connection:
            total_price += flight.base_price + (bags_count * flight.bag_price)
        return total_price

    @staticmethod
    def _travel_time_calc(connection: List[Flight]) -> str:
        """
        Calculates the full travel time for the specified connection (list of subsequent flights).

        :param connection: List of subsequent flights between two airports.
        :return: Returns the time in string format: hh:mm:ss.
        """
        duration = connection[-1].arrival_datetime_format - connection[0].departure_datetime_format
        seconds = int(duration.total_seconds())
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)

    def search_flights(self, start: Airport, finish: Airport,
                       nr_bags: int) -> List[Dict[str, Union[List, int, str, float]]]:
        """
        Searches the possible connections between two airports and formats the found connections as desired.
        Sorts the connections based on the travel price in ascending order.

        :param start: Origin airport defined by the user.
        :param finish: Destination airport defined by the user.
        :param nr_bags: Number of bags defined by the user.
        :return: Sorted and formatted list of connections.
        """
        found_flights = []
        flight_lists = self._flight_search_calc(start, finish, nr_bags, [])
        for flight_list in flight_lists:
            formatted_flight_list = self._format_flights_to_list(flight_list)
            current_route = {'flight': formatted_flight_list,
                             'bags_allowed': min([flight.bags_allowed for flight in flight_list]),
                             'bags_count': nr_bags,
                             'destination': finish.name,
                             'origin': start.name,
                             'total_price': self._total_price_calc(flight_list, nr_bags),
                             'travel_time': self._travel_time_calc(flight_list)
                             }
            found_flights.append(current_route)
        return sorted(found_flights, key=lambda k: k['total_price'])
