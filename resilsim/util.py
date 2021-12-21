import csv
import math
import numpy as np

import resilsim.settings as settings
import plotly.graph_objects as go
import scipy.stats as st


def distance(lat1, lon1, lat2, lon2):
    r = 6378.137
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)

    diff_lat = lat2 - lat1
    diff_lon = lon2 - lon1

    a = math.sin(diff_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(diff_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = r * c
    return d * 1000


def isolated_users(ue):
    counter = 0
    for user in ue:
        if user.link is None:
            counter += 1
    return counter / len(ue)


def received_service(ue):
    percentages = []

    for user in ue:
        if user.link is not None:
            percentages.append(
                1 if user.link.shannon_capacity / user.requested_capacity > 1
                else user.link.shannon_capacity / user.requested_capacity)
        else:
            percentages.append(0)

    return sum(percentages) / len(percentages) if len(percentages) != 0 else 0


def received_service_half(ue):
    counter = 0

    for user in ue:
        if user.link is not None:
            if user.link.shannon_capacity / user.requested_capacity >= 0.5:
                counter += 1

    return counter / len(ue)


def avg_distance(ue):
    distances = []
    for user in ue:
        if user.link:
            distances.append(user.link.distance)

    return sum(distances) / len(distances) if len(distances) != 0 else None  # not 1 user is connected so infinite


def isolated_systems(base_stations):
    systems = 0
    bs_copy = base_stations[:]
    while len(bs_copy) != 0:
        systems += 1
        first = bs_copy.pop(0)
        checked = [link.other(first) for link in first.connected_BS[:]]
        while len(checked) != 0:
            second = checked.pop(0)
            if second in bs_copy:
                bs_copy.remove(second)
                checked = checked + [link.other(second) for link in second.connected_BS[:]]

    return systems


def snr_averages(ue):
    snrs = []
    for user in ue:
        if user.link:
            snrs.append(user.snr)
        else:
            snrs.append(0)
    return sum(snrs) / len(snrs) if len(snrs) > 0 else 0


def active_base_stations(bs):
    return sum([1 if bs.functional >= 0.2 else 0 for bs in bs])


def connected_ue_bs(base_stations):
    return sum([len(bs.connected_UE) for bs in base_stations]) / len(base_stations)


def to_pwr(db):
    return 10 ** (db / 10)


def to_db(pwr):
    return 10 * math.log10(pwr)


def avg(lst):
    length = 0
    total_sum = 0

    for i in lst:
        if i is not None:
            length += 1
            total_sum += i

    return total_sum / length if length > 0 else -1


def get_unit(index):
    if index == 0:
        return "Isolated Users (%)"
    elif index == 1:
        return "Satisfaciton level (%)"
    elif index == 2:
        return "50% Satisfaction level (%)"
    elif index == 3:
        return "Avg. Distance to BS (meters)"
    elif index == 4:
        return "#Isolated Systems"
    elif index == 5:
        return "#Active BS"
    elif index == 6:
        return "Avg. SNR (ratio)"
    elif index == 7:
        return "Avg. #users connected to BS"
    else:
        return "Error"


def get_x_values():
    if settings.LARGE_DISASTER:
        return [settings.RADIUS_PER_SEVERITY * r for r in range(settings.SEVERITY_ROUNDS)], "Radius disaster (meters)"
    elif settings.MALICIOUS_ATTACK:
        return [(settings.FUNCTIONALITY_DECREASED_PER_SEVERITY * s) for s in
                range(settings.SEVERITY_ROUNDS)], "Functionality decreased of BS"
    elif settings.ENVIRONMENTAL_RISK:
        return [s * settings.ENV_SIGNAL_DEDUC_PER_SEVERITY for s in
                range(settings.SEVERITY_ROUNDS)], "Signal strength reduced (%)"
    elif settings.INCREASING_REQUESTED_DATA:
        return [s for s in range(settings.SEVERITY_ROUNDS)], "Severity level of increasing data"


def create_plot(city_results):
    x_values, unit = get_x_values()

    for z in [0, 1]:
        fig = go.Figure()
        for city in city_results:
            results = [m.get_metrics() for m in city_results[city]]
            errors = [m.get_cdf() for m in city_results[city]]
            fig.add_trace(go.Scatter(
                x=x_values,
                y=[r[z] for r in results if r[z] is not None],
                mode='lines+markers',
                name=str(city),
                error_y=dict(
                    type='data',
                    array=[e[z] for e in errors if e[z] is not None],
                    visible=True
                )
            ))
        fig.update_layout(xaxis_title=unit, yaxis_title=get_unit(z),
                          legend=dict(yanchor="bottom", y=0.05, xanchor="left", x=0.05))
        fig.show()

    pass


def cdf(data, confidence=0.95):
    processed_data = [d for d in data if d is not None]
    if len(processed_data) == 0 or len(processed_data) == 1:
        return 0

    mean, se = np.mean(processed_data), st.sem(processed_data)
    h = se * st.t.ppf((1 + confidence) / 2, len(processed_data) - 1)
    return h


def create_new_file():
    with open(settings.SAVE_CSV_PATH, 'w', newline='') as f:
        fieldnames = ['city', 'severity', 'isolated_users', 'received_service', 'received_service_half', 'avg_distance',
                      'isolated_systems', 'active_base_stations', 'avg_snr', 'connected_UE_BS']
        csv_writer = csv.writer(f)
        csv_writer.writerow(fieldnames)


def save_data(city, metrics):
    with open(settings.SAVE_CSV_PATH, 'a', newline='') as f:
        csv_writer = csv.writer(f)
        for i in range(settings.SEVERITY_ROUNDS):
            metric = metrics[i].csv_export()
            for m in metric:
                csv_writer.writerow([city.name, i] + m)
