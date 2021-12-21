from pathlib import Path
import os

ROOT_DIR = Path(__file__).parent

BS_PATH = os.path.join(ROOT_DIR, "data", "antennas.json")
CITY_PATH = os.path.join(ROOT_DIR, "data", "city.csv") #TODO add city centre to the data

SAVE_IN_CSV = True
CREATE_PLOT = False
SAVE_CSV_PATH = os.path.join(ROOT_DIR, "results", "normal.csv")

AMOUNT_THREADS = 22

UE_CAPACITY_MIN = 10
UE_CAPACITY_MAX = 100

SEVERITY_ROUNDS = 10
ROUNDS_PER_SEVERITY = 2
ROUNDS_PER_USER = 100

# CITY SPECIFIC PARAMETERS
ACTIVITY = 0.007

#BASE STATION PROPERTIES
BS_BS_RANGE = 4000 #TODO what is this used for

MCL = 70 #in db -> seems high for minimum coupling loss???
HEIGHT_ABOVE_BUILDINGS = 20
CARRIER_FREQUENCY = 2000 # TODO remove?
BASE_POWER = 43 #TODO remove
G_TX = 15 #TODO adapt to be a base number that can be increased by beamforming
G_RX = 0

OPEN_CHANNELS = 5 # TODO remove -> is replaced by knowledge about the number of channels in the new data set
CHANNEL_BANDWIDTHS = [20,15,10,5,3,1.4] # TODO find the source/find source for this for 5G

SIGNAL_NOISE = -100 # TODO why 100?

# RISKS ENABLED
#TODO move to more logical location?

# if a large disaster occured, for instance a natural disaster or a depending failure
LARGE_DISASTER = False
POWER_OUTAGE = False
RADIUS_PER_SEVERITY = 1000

# malicious attacks on a certain region, for instance a DDoS
MALICIOUS_ATTACK = False
PERCENTAGE_BASE_STATIONS = 0.5
FUNCTIONALITY_DECREASED_PER_SEVERITY = 0.1

# small individual errors on some base stations
ENVIRONMENTAL_RISK = False
PERCENTAGE_RANGE_BS = 0.8
ENV_SIGNAL_DEDUC_PER_SEVERITY = 0.05


# increasing requested data
INCREASING_REQUESTED_DATA = False
OFFSET = 10
DATA_PER_SEV = 10
WINDOW_SIZE = 10
















