import util
from objects.City import City
from objects.Metrics import Metrics
import resilsim.settings as settings
import csv
import json
import plotly.graph_objects as go
import os
import plotly.io as pio
pio.kaleido.scope.mathjax = None

def load():

    file = os.path.join(settings.ROOT_DIR, "results", "disaster.csv")
#    file = os.path.join(settings.ROOT_DIR, "results", "disaster_power.csv")

    # Get all city names
    all_cities = []
    with open(settings.CITY_PATH) as f:
        cities = json.load(f)
        for city in cities:
            all_cities.append(city.get('name'))

    sub_city_results = dict()

    print("importing file")
    with open(file, newline='') as f:

        filereader = csv.DictReader(f)
        for row in filereader:

            city = str(row["city"])
            if city not in all_cities:
                continue
            severity = int(row["severity"])
            isolated_users = float(row["isolated_users"]) if row["isolated_users"] != '' else None
            received_service = float(row["received_service"]) if row["received_service"] != '' else None
            received_service_half = float(row["received_service_half"]) if row["received_service_half"] != '' else None
            avg_distance = float(row["avg_distance"]) if row["avg_distance"] != '' else None
            isolated_systems = float(row["isolated_systems"]) if row["isolated_users"] != '' else None
            active_base_stations = float(row["active_base_stations"]) if row["active_base_stations"] else None
            avg_snr = float(row["avg_snr"]) if row["avg_snr"] else None
            connected_UE_BS = float(row["connected_UE_BS"]) if row["connected_UE_BS"] else None
            active_channels = float(row["active_channels"]) if row["active_channels"] else None

            if city not in sub_city_results:
                sub_city_results[city] = []

            while severity >= len(sub_city_results[city]):
                sub_city_results[city].append(Metrics())

            sub_city_results[city][severity].add_metric((isolated_users,
                                                         received_service,
                                                         received_service_half,
                                                         avg_distance,
                                                         isolated_systems,
                                                         active_base_stations,
                                                         avg_snr,
                                                         connected_UE_BS,
                                                         active_channels))

    city_results = dict()
    for city in sub_city_results:
        city_results[City(city,0,0,0,0,0)] = sub_city_results[city]

    print("Plotting results")
#    util.create_plot(city_results)

    x_values, unit = util.get_x_values()

    #    for z in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
    for z in [0, 1]:
        fig = go.Figure()
        for city in city_results:
            results = [m.get_metrics() for m in city_results[city]]
            errors = [m.get_cdf() for m in city_results[city]]
            fig.add_trace(go.Scatter(
                x=x_values,
                y=[100*r[z] for r in results if r[z] is not None],
                mode='lines+markers',
                name=str(city),
                error_y=dict(
                    type='data',
                    array=[100*e[z] for e in errors if e[z] is not None],
                    visible=True
                )
            ))
        if z == 0:
            fig.update_layout(xaxis_title=unit, yaxis_title=util.get_unit(z),
                              legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.05))
        else:
            fig.update_layout(xaxis_title=unit, yaxis_title=util.get_unit(z),
                              legend=dict(yanchor="bottom", y=0.05, xanchor="left", x=0.05))
        fig.update_layout(xaxis_title_font_size=20, yaxis_title_font_size=20)

        fig.show()
        if not os.path.exists("images"):
            os.mkdir("images")
        nt = 'satisfaction' if z == 1 else 'isolated'
        fig.write_image(f'images/disaster_{nt}.pdf')
#        fig.write_image(f'images/disaster_power_{nt}.pdf')


def create_plot_mmwave_comp():
#    files = [('disaster.csv',0),('disaster_mmwave_25.csv',25),('disaster_mmwave_50.csv',50),('disaster_mmwave_75.csv',75),('disaster_mmwave_100.csv',100)]
    files = [('disaster.csv', 0), ('disaster_mmwave_50.csv', 50), ('disaster_mmwave_100.csv',100)]
#    files = [('disaster_power.csv', 0), ('disaster_power_mmwave_50.csv', 50), ('disaster_power_mmwave_100.csv', 100)]

# Get all city names
    all_cities = []
    with open(settings.CITY_PATH) as f:
        cities = json.load(f)
        for city in cities:
            all_cities.append(city.get('name'))

    results = dict()

    for mmwave_name in files:
        name = os.path.join(settings.ROOT_DIR, 'results', mmwave_name[0])
        print(f"importing file {name}")
        sub_city_results = dict()

        with open(name, newline='') as f:
            filereader = csv.DictReader(f)
            for row in filereader:
                city = str(row["city"])
                if city not in all_cities:
                    continue
                severity = int(row["severity"])
                isolated_users = float(row["isolated_users"]) if row["isolated_users"] != '' else None
                received_service = float(row["received_service"]) if row["received_service"] != '' else None
                received_service_half = float(row["received_service_half"]) if row["received_service_half"] != '' else None
                avg_distance = float(row["avg_distance"]) if row["avg_distance"] != '' else None
                isolated_systems = float(row["isolated_systems"]) if row["isolated_users"] != '' else None
                active_base_stations = float(row["active_base_stations"]) if row["active_base_stations"] else None
                avg_snr = float(row["avg_snr"]) if row["avg_snr"] else None
                connected_UE_BS = float(row["connected_UE_BS"]) if row["connected_UE_BS"] else None
                active_channels = float(row["active_channels"]) if row["active_channels"] else None

                if city not in sub_city_results:
                    sub_city_results[city] = []

                while severity >= len(sub_city_results[city]):
                    sub_city_results[city].append(Metrics())

                sub_city_results[city][severity].add_metric((isolated_users,
                                                             received_service,
                                                             received_service_half,
                                                             avg_distance,
                                                             isolated_systems,
                                                             active_base_stations,
                                                             avg_snr,
                                                             connected_UE_BS,
                                                             active_channels))

        city_results = dict()
        for city in sub_city_results:
            city_results[City(city,0,0,0,0,0)] = sub_city_results[city]
        results[mmwave_name[1]] = city_results

    print("Plotting results")

    # plot the stuff
    x_values, unit = util.get_x_values()


    for z in [0, 1]:
#        fig = go.Figure()  # when all cities in one fig
        for city in all_cities:
            fig = go.Figure()  # when one city per fig
            for r in results.keys():  # loop over mmwave deployments
                city_results = results.get(r)
                for c in city_results:  # loop over cities
                    if c.name == city:
                        metrics = [m.get_metrics() for m in city_results[c]]
                        errors = [m.get_cdf() for m in city_results[c]]
                        fig.add_trace(go.Scatter(
                            x=x_values,
                            y=[100*m[z] for m in metrics if m[z] is not None],
                            mode='lines+markers',
                            name=f"{city}: {r}%",
                            error_y=dict(
                                type='data',
                                array=[100*e[z] for e in errors if e[z] is not None],
                                visible=True
                            )
                        ))
            if z == 0:
                fig.update_layout(xaxis_title=unit, yaxis_title=util.get_unit(z),
                                  legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.05))
            else:
                fig.update_layout(xaxis_title=unit, yaxis_title=util.get_unit(z),
                                  legend=dict(yanchor="bottom", y=0.05, xanchor="left", x=0.05))
            fig.update_layout(xaxis_title_font_size=20, yaxis_title_font_size=20)

            if not os.path.exists("images"):
                os.mkdir("images")
            nt = 'satisfaction' if z == 1 else 'isolated'
            fig.write_image(f'images/disaster_mmwave_{city}_{nt}.pdf')
#            fig.write_image(f'images/disaster_power_mmwave_{city}_{nt}.pdf')

            fig.update_layout(title=city)
            fig.show()  # when one city per fig
#        fig.show()  # when all cities in one fig

if __name__ == '__main__':
    create_plot_mmwave_comp()
    load()
