import resilsim.objects.Link as Link
from resilsim.objects.Metrics import Metrics
from resilsim.objects.UE import UserEquipment
from resilsim.settings import *
import numpy as np
import resilsim.util as util
import csv
import json
import resilsim.objects.BaseStation as bso
from resilsim.objects.City import City

from multiprocessing import Pool


def main():
    if SAVE_IN_CSV:
        util.create_new_file()

    all_cities = load_cities()
    city_results = dict()

    for city in all_cities:
        print("Starting simulation for city:{}".format(city.name))
        base_stations = load_bs(city.min_lat, city.min_lon, city.max_lat, city.max_lon)
        if ENVIRONMENTAL_RISK:
            for bs in base_stations:
                bs.range_bs = bs.range_bs * PERCENTAGE_RANGE_BS
        results = []
        for s in range(SEVERITY_ROUNDS):
            results.append(Metrics())

        argument_list = arg_list(city, base_stations)

        with Pool(AMOUNT_THREADS) as p:
            res = p.starmap(pool_func, argument_list)

            for r in res:
                for m in range(len(r)):
                    results[m].add_metrics_object(r[m])

        print("")
        for r in results:
            print(r)
        print("------------------------------------------------------\n")
        city_results[city] = results

        if SAVE_IN_CSV:
            util.save_data(city, results)

    if CREATE_PLOT:
        util.create_plot(city_results)


def arg_list(city, base_stations):
    """
    Creates an argument list with the needed arguments for each round
    :param city: The city list used as argument ofr each round
    :param base_stations: The base stations used as argument each round
    :return: List((Int,BaseStation,City)) For each round a unique basestation and city
    """
    res = []
    for u in range(ROUNDS_PER_USER):
        copy_bs = [bs.get_copy() for bs in base_stations]
        res.append((u, copy_bs, city))
    return res


def pool_func(u, base_stations, city):
    """
    Function to be called by the pool manager
    :param u: the round
    :param base_stations: the basestations for the round
    :param city: the city
    :return: a dictionary with for each severity the resilience metrics
    """
    results = []
    for s in range(SEVERITY_ROUNDS):
        results.append(Metrics())

    links = connected_base_stations(base_stations)
    UE = create_ue(city)
    connect_ue_bs(UE, base_stations)
    for severity in range(SEVERITY_ROUNDS):
        for r in range(ROUNDS_PER_SEVERITY):
            print("\rStarting simulation:({},{},{})".format(u, severity, r), end='')
            # print("Resetting base stations and UE")
            reset_all(base_stations, UE)
            # print("Failing base stations and links")
            fail(base_stations, UE, links, city, severity)
            # print("Connecting UE to BS again")
            connect_ue_bs(UE, base_stations, severity)
            # print("Directing capacities to the users")
            # print("Creating resilience metrics after failure")
            values = simulate(base_stations, UE, links)
            results[severity].add_metric(values)

    return results


def connected_base_stations(base_stations):
    """
    Shows all basestations connected
    :param base_stations: basestation for which to show the connections
    :return: List[Link]
    """
    links = list()
    len_base_stations = len(base_stations)
    for i in range(len_base_stations):
        first = base_stations[i]
        for j in range(i + 1, len_base_stations):
            second = base_stations[j]

            if first.radio != second.radio:
                continue

            dist = util.distance(first.lat, first.lon, second.lat, second.lon)
            if dist < BS_BS_RANGE:
                link = first + second
                links.append(link)
    return links


# TODO change distribution
def create_ue(city):
    """
    Creates the user equipment
    :param city: City for which to create the UEs
    :return: list of UEs
    """
    all_UE = list()
    all_lon = np.random.uniform(city.min_lon, city.max_lon, city.population_amount)
    all_lat = np.random.uniform(city.min_lat, city.max_lat, city.population_amount)
    all_cap = np.random.randint(UE_CAPACITY_MIN, UE_CAPACITY_MAX, city.population_amount)
    for i in range(city.population_amount):
        lon = all_lon[i]
        lat = all_lat[i]

        new_UE = UserEquipment(i, lon, lat, all_cap[i])
        all_UE.append(new_UE)

    return all_UE


def connect_ue_bs(ue, base_stations, severity=0):
    for user in ue:
        BS_in_area = []
        for bs in base_stations:
            dist = util.distance(user.lat, user.lon, bs.lat, bs.lon)
            if dist < bs.range_bs and bs.functional > (1 / OPEN_CHANNELS):
                BS_in_area.append((bs, dist))

        BS_in_area = sorted(BS_in_area, key=lambda x: x[1])
        for bs, dist in BS_in_area:
            if ENVIRONMENTAL_RISK:
                new_link = Link.BS_UE_Link(user, bs, dist, signal_deduction=1 - ENV_SIGNAL_DEDUC_PER_SEVERITY * severity)
            else:
                new_link = Link.BS_UE_Link(user, bs, dist)

            if new_link.bandwidthneeded is None:
                continue
            user.set_base_station(new_link)
            bs.add_ue(new_link)
            if bs.overflow:
                bs.remove_ue(new_link)
                user.reset()
                bs.direct_capacities()
            else:
                break


def fail(base_stations, ue, links, city, severity):
    if LARGE_DISASTER:
        radius = severity * RADIUS_PER_SEVERITY
        random_lat = np.random.uniform(city.min_lat, city.max_lat, 1)[0]
        random_lon = np.random.uniform(city.min_lon, city.max_lon, 1)[0]

        for bs in base_stations:
            dist = util.distance(bs.lat, bs.lon, random_lat, random_lon)
            if dist < radius:
                if POWER_OUTAGE:
                    bs.malfunction(0)
                else:
                    # When closer to the epicentre the BS will function less good
                    bs.malfunction((dist / radius) ** 2)

    elif MALICIOUS_ATTACK:
        affected_bs = np.random.choice(base_stations, round(len(base_stations) * PERCENTAGE_BASE_STATIONS),
                                       replace=False)
        for bs in affected_bs:
            bs.malfunction(1 - (severity * FUNCTIONALITY_DECREASED_PER_SEVERITY))

    elif INCREASING_REQUESTED_DATA:
        x = OFFSET + DATA_PER_SEV * severity
        all_cap = np.random.randint(x, x + WINDOW_SIZE, city.population_amount)
        for i in range(len(ue)):
            user = ue[i]
            cap = all_cap[i]
            user.requested_capacity = cap


def simulate(base_stations, ue, links):
    iso_users = util.isolated_users(ue)
    percentage_received_service = util.received_service(ue)

    percentage_received_service_half = util.received_service_half(ue)
    average_distance_to_bs = util.avg_distance(ue)

    iso_systems = util.isolated_systems(base_stations)

    active_base_stations = util.active_base_stations(base_stations)

    avg_snr = util.snr_averages(ue)

    connected_UE_BS = util.connected_ue_bs(base_stations)

    return iso_users, percentage_received_service, percentage_received_service_half, average_distance_to_bs, iso_systems, active_base_stations, avg_snr, connected_UE_BS


def reset_all(base_stations, ue):
    for bs in base_stations:
        bs.reset()

    for user in ue:
        user.reset()


def load_cities():
    all_cities = list()
    with open(CITY_PATH, newline='') as f:
        filereader = csv.DictReader(f)
        for row in filereader:
            all_cities.append(City(row["name"], row["min_lat"], row["min_lon"], row["max_lat"], row["max_lon"],
                                   row["population"]))

    return all_cities


def load_bs(min_lat, min_lon, max_lat, max_lon):
    all_basestations = list()
    with open(BS_PATH) as f:
        bss = json.load(f)
        # Loop over base-stations
        for bs in bss:
            bs_lon = float(bs.get('X'))
            bs_lat = float(bs.get('Y'))
            if min_lon <= bs_lon <= max_lon and min_lat <= bs_lat <= max_lat:
                if bs.get("HOOFDSOORT") == "LTE":
                    radio = util.BaseStationRadioType.LTE
                elif bs.get("HOOFDSOORT") == "5G NR":
                    radio = util.BaseStationRadioType.NR
                else:
                    radio = None # TODO error when this is true
                new_bs = bso.BaseStation(radio, bs_lon, bs_lat, bs.get('antennes')[0].get("Hoogte"))
                for antenna in bs.get("antennes"):
                    new_bs.add_channel(antenna.get("Frequentie"), antenna.get("Vermogen"))
                all_basestations.append(new_bs)
    return all_basestations


# def load_bs(min_lat, min_lon, max_lat, max_lon):
#     all_basestations = list()
#     all_basestations_dict = dict()
#
#     with open(BS_PATH, newline='') as f:
#         filereader = csv.DictReader(f)
#         for row in filereader:
#             lon = float(row["lon"])
#             lat = float(row["lat"])
#             if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
#                 if row["area"] not in all_basestations_dict:
#                     new_basestation = bs.BaseStation(row["radio"], row["mcc"], row["net"], row["area"], row["cell"], row["unit"], lon, lat, row["range"], row["samples"], row["changeable"], row["created"], row["updated"], row["averageSignal"])
#                     all_basestations_dict[row["area"]] = new_basestation
#                     all_basestations.append(new_basestation)
#                 else:
#                     # TODO: MAYBE COMBINE COORDINATES
#                     pass
#     return all_basestations

if __name__ == '__main__':
    main()
