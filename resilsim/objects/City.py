from resilsim.settings import ACTIVITY


class City:
    def __init__(self, name, min_lat, min_lon, max_lat, max_lon, population):
        self.name = name
        self.min_lat = float(min_lat)
        self.min_lon = float(min_lon)
        self.max_lat = float(max_lat)
        self.max_lon = float(max_lon)
        self.population = int(population)
        self.active_users = int((ACTIVITY * self.population) // 1)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "%s(name=%r, population=%r, active_users=%r, min_lat=%r, max_lat=%r, min_lon=%r, max_lon=%r)" \
               % (self.__class__, self.name, self.population, self.active_users,
                  self.min_lat, self.max_lat, self.min_lon, self.max_lon)
