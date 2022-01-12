import copy

from resilsim.objects.Metrics import Metrics
from resilsim.objects.UE import UserEquipment
import resilsim.settings as settings
import numpy as np
import resilsim.util as util
import json
import resilsim.objects.BaseStation as BSO
import resilsim.objects.City as City

from multiprocessing import Pool


def main():
    if settings.SAVE_IN_CSV:
        util.create_new_file()

    all_cities = load_cities()
    city_results = dict()

    for city in all_cities:
        print("Starting simulation for city:{}".format(city.name))
        base_stations = load_bs(city)
        s = 0
        for b in base_stations:
            s += len(b.channels)
        print(
            f"number of channels:{s}, max users per channel = {base_stations[0].channels[0].max_devices}; users = {city.active_users}; max users connecting: {base_stations[0].channels[0].max_devices * s}")
        results = []
        for s in range(settings.SEVERITY_ROUNDS):
            results.append(Metrics())

        argument_list = arg_list(city, base_stations)

        # Single threaded
        #        for (u,bs,c) in argument_list:
        #            res = pool_func(u,bs,c)
        #            for m in range(len(res)):
        #                results[m].add_metrics_object(res[m])

        # multi threaded
        with Pool(settings.AMOUNT_THREADS) as p:
            res = p.starmap(pool_func, argument_list)

            for r in res:
                for m in range(len(r)):
                    results[m].add_metrics_object(r[m])

        print("")
        for r in results:
            print(r)
        print("------------------------------------------------------\n")
        city_results[city] = results

        if settings.SAVE_IN_CSV:
            util.save_data(city, results)

    if settings.CREATE_PLOT:
        util.create_plot(city_results)


def arg_list(city, base_stations):
    """
    Creates an argument list with the needed arguments for each round
    :param city: The city list used as argument ofr each round
    :param base_stations: The base stations used as argument each round
    :return: List((Int,BaseStation,City)) For each round a unique basestation and city
    """
    res = []
    for u in range(settings.ROUNDS_PER_USER):
        # copy_bs = [bs.get_copy() for bs in base_stations]
        copy_bs = copy.deepcopy(base_stations)
        res.append((u, copy_bs, city))
    return res


def pool_func(u, base_stations, city):
    """
    Function to be called by the pool manager
    :param u: the round per user
    :param base_stations: the basestations for the round
    :param city: the city
    :return: a dictionary with for each severity the resilience metrics
    """
    results = []
    for s in range(settings.SEVERITY_ROUNDS):
        results.append(Metrics())

    links = connected_base_stations(base_stations)
    UE = create_ue(city)
    for severity in range(settings.SEVERITY_ROUNDS):
        for r in range(settings.ROUNDS_PER_SEVERITY):
            print("\rStarting simulation:({},{},{})".format(u, severity, r), end='')
            # print("Resetting base stations and UE")
            reset_all(base_stations, UE)
            # print("Failing base stations and links")
            if not fail(base_stations, UE, links, city, severity):
                print("Nothing to fail")
                continue  # Nothing to fail due to no events enabled
            # print("Connecting UE to BS again")
            connect_ue_bs(UE, base_stations, severity)
            # print("Directing capacities to the users")
            # print("Creating resilience metrics after failure")
            values = simulate(base_stations, UE, links)
            results[severity].add_metric(values)

    return results


def connected_base_stations(base_stations):
    links = list()
    len_base_stations = len(base_stations)
    for i in range(len_base_stations):
        first = base_stations[i]
        for j in range(i + 1, len_base_stations):
            second = base_stations[j]

            if first.radio != second.radio:
                continue

            dist = util.distance(first.lat, first.lon, second.lat, second.lon)
            if dist < settings.BS_RANGE:
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
    all_users = city.active_users
    all_lon = np.random.uniform(city.min_lon, city.max_lon, all_users)
    all_lat = np.random.uniform(city.min_lat, city.max_lat, all_users)
    all_cap = np.random.randint(settings.UE_CAPACITY_MIN, settings.UE_CAPACITY_MAX, all_users)
    for i in range(all_users):
        lon = all_lon[i]
        lat = all_lat[i]

        new_UE = UserEquipment(i, lon, lat, all_cap[i])
        all_UE.append(new_UE)

    return all_UE


def connect_ue_bs(ue, base_stations, severity=0):
    for user in ue:
        BS_in_area = []
        # Collect all BS within range
        for bs in base_stations:
            dist = util.distance(user.lat, user.lon, bs.lat, bs.lon)
            if dist <= settings.BS_RANGE:
                BS_in_area.append((bs, dist))

        # Sort BS in area on from closest to farthest
        BS_in_area = sorted(BS_in_area, key=lambda x: x[1])
        # Loop over BSs connecting when possible
        for bs, dist in BS_in_area:
            if bs.add_ue(user):
                break


def fail(base_stations, ue, links, city, severity):
    if settings.LARGE_DISASTER:
        radius = severity * settings.RADIUS_PER_SEVERITY
        random_lat = np.random.uniform(city.min_lat, city.max_lat, 1)[0]
        random_lon = np.random.uniform(city.min_lon, city.max_lon, 1)[0]

        for bs in base_stations:
            dist = util.distance(bs.lat, bs.lon, random_lat, random_lon)
            if dist < radius:
                if settings.POWER_OUTAGE:
                    bs.malfunction(0)
                else:
                    # When closer to the epicentre the BS will function less
                    bs.malfunction((dist / radius) ** 2)

    elif settings.MALICIOUS_ATTACK:
        affected_bs = np.random.choice(base_stations, round(len(base_stations) * settings.PERCENTAGE_BASE_STATIONS),
                                       replace=False)
        for bs in affected_bs:
            bs.malfunction(1 - (severity * settings.FUNCTIONALITY_DECREASED_PER_SEVERITY))

    elif settings.INCREASING_REQUESTED_DATA:
        x = settings.OFFSET + settings.DATA_PER_SEV * severity
        all_cap = np.random.randint(x, x + settings.WINDOW_SIZE, city.active_users)
        for i in range(len(ue)):
            user = ue[i]
            cap = all_cap[i]
            user.requested_capacity = cap

    else:
        return severity == 0

    return True


def simulate(base_stations, ue, links):
    iso_users = util.isolated_users(ue)
    percentage_received_service = util.received_service(ue)

    percentage_received_service_half = util.received_service_half(ue)
    average_distance_to_bs = util.avg_distance(ue)

    iso_systems = util.isolated_systems(base_stations)

    active_base_stations = util.active_base_stations(base_stations)

    avg_snr = util.snr_averages(ue)

    connected_UE_BS = util.connected_ue_bs(base_stations)

    active_channels = util.active_channels(base_stations)

    return iso_users, percentage_received_service, percentage_received_service_half, average_distance_to_bs, iso_systems, active_base_stations, avg_snr, connected_UE_BS, active_channels


def reset_all(base_stations, ue):
    for bs in base_stations:
        bs.reset()

    for user in ue:
        user.reset()


def load_cities():
    all_cities = list()
    with open(settings.CITY_PATH) as f:
        cities = json.load(f)
        for city in cities:
            new_city_name = city.get('name')
            new_city_population = city.get('population')
            new_city_rma_area = None
            new_city_uma_area = None
            new_city_umi_area = None
            if 'RMa' in city:
                rma = city.get('RMa')
                min_lat = float(rma.get('min_x'))
                min_lon = float(rma.get('min_y'))
                max_lat = float(rma.get('max_x'))
                max_lon = float(rma.get('max_y'))
                new_city_rma_area = City.Area(min_lat, min_lon, max_lat, max_lon)
                new_city_rma_area.area_type = util.AreaType.RMA
            if 'UMa' in city:
                uma = city.get('UMa')
                min_lat = float(uma.get('min_x'))
                min_lon = float(uma.get('min_y'))
                max_lat = float(uma.get('max_x'))
                max_lon = float(uma.get('max_y'))
                new_city_uma_area = City.Area(min_lat, min_lon, max_lat, max_lon)
                new_city_uma_area.area_type = util.AreaType.UMA
            if 'UMi' in city:
                umi = city.get('UMi')
                min_lat = float(umi.get('min_x'))
                min_lon = float(umi.get('min_y'))
                max_lat = float(umi.get('max_x'))
                max_lon = float(umi.get('max_y'))
                new_city_umi_area = City.Area(min_lat, min_lon, max_lat, max_lon)
                new_city_umi_area.area_type = util.AreaType.UMI
            new_city = None
            if new_city_rma_area is not None:
                new_city = City.City(new_city_name, new_city_rma_area.min_lat, new_city_rma_area.min_lon,
                                     new_city_rma_area.max_lat, new_city_rma_area.max_lon, new_city_population)
            elif new_city_uma_area is not None:
                new_city = City.City(new_city_name, new_city_uma_area.min_lat, new_city_uma_area.min_lon,
                                     new_city_uma_area.max_lat, new_city_uma_area.max_lon, new_city_population)
            elif new_city_umi_area is not None:
                new_city = City.City(new_city_name, new_city_umi_area.min_lat, new_city_umi_area.min_lon,
                                     new_city_umi_area.max_lat, new_city_umi_area.max_lon, new_city_population)
            new_city.rma_area = new_city_rma_area
            new_city.uma_area = new_city_uma_area
            new_city.umi_area = new_city_umi_area
            all_cities.append(new_city)
    return all_cities


# TODO add BSs for area larger than city?
def load_bs(city):
    min_lat, min_lon, max_lat, max_lon = city.min_lat, city.min_lon, city.max_lat, city.max_lon
    all_basestations = list()
    with open(settings.BS_PATH) as f:
        bss = json.load(f)
        # Loop over base-stations
        for bs in bss:
            bs_lat = float(bs.get('X'))
            bs_lon = float(bs.get('Y'))
            if min_lon <= bs_lon <= max_lon and min_lat <= bs_lat <= max_lat:
                if bs.get("HOOFDSOORT") == "LTE":
                    radio = util.BaseStationRadioType.LTE
                elif bs.get("HOOFDSOORT") == "5G NR":
                    radio = util.BaseStationRadioType.NR
                else:
                    radio = None  # TODO error when this is true
                # TODO change area when city contains that data properly
                h = bs.get('antennes')[0].get("Hoogte")
                h = util.str_to_float(h)
                # print(bs.get('GEMNAAM'))
                new_bs = BSO.BaseStation(bs.get('ID'), radio, bs_lon, bs_lat, h,
                                         City.Area(min_lat, min_lon, max_lat, max_lon))
                new_bs.area = city.area(bs_lon, bs_lat)
                for antenna in bs.get("antennes"):
                    f = util.str_to_float(antenna.get("Frequentie"))
                    p = util.str_to_float(antenna.get("Vermogen"))
                    new_bs.add_channel(f, p)
                all_basestations.append(new_bs)

    return all_basestations


if __name__ == '__main__':
    main()
