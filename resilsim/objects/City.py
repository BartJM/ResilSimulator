from resilsim.settings import ACTIVITY
import resilsim.util as util


class City:
    def __init__(self, name, min_lat, min_lon, max_lat, max_lon, population):
        self.name = name
        self.min_lat = float(min_lat)
        self.min_lon = float(min_lon)
        self.max_lat = float(max_lat)
        self.max_lon = float(max_lon)
        self.min_lat_uma = None 
        self.min_lon_uma = None 
        self.max_lat_uma = None 
        self.max_lon_uma = None 
        self.min_lat_umi = None 
        self.min_lon_umi = None 
        self.max_lat_umi = None 
        self.max_lon_umi = None 
        self.areas_defined = False
        self.population = int(population)
        self.active_users = int((ACTIVITY * self.population) // 1)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "%s(name=%r, population=%r, active_users=%r, min_lat=%r, max_lat=%r, min_lon=%r, max_lon=%r)" \
               % (self.__class__, self.name, self.population, self.active_users,
                  self.min_lat, self.max_lat, self.min_lon, self.max_lon)

    def area_type(self, lon, lat):
        # gives area type for the given location
        if not (self.min_lon <= lon <= self.max_lon and self.min_lat <= lat <= self.max_lat):
            raise ValueError("Location not within city")
        else:
            # Check if city is specified otherwise default to UMa
            if not self.areas_defined:
                return util.AreaType.UMA
            # Check for area type
            if self.min_lon_umi <= lon <= self.max_lon_umi and self.min_lat_umi <= lat <= self.max_lat_umi:
                return util.AreaType.UMI
            elif self.min_lon_uma <= lon <= self.max_lon_uma and self.min_lat_uma <= lat <= self.max_lat_uma:
                return util.AreaType.UMA
            return util.AreaType.RMA

