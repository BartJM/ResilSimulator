from pathlib import Path
import os

ROOT_DIR = Path(__file__).parent

BS_PATH = os.path.join(ROOT_DIR, "data", "antennas.json")
CITY_PATH = os.path.join(ROOT_DIR, "data", "city.json")

SAVE_IN_CSV = True
CREATE_PLOT = False
SAVE_CSV_PATH = os.path.join(ROOT_DIR, "results", "disaster.csv")

AMOUNT_THREADS = None

UE_CAPACITY_MIN = 10
UE_CAPACITY_MAX = 100

SEVERITY_ROUNDS = 10  # 10
ROUNDS_PER_SEVERITY = 2  # 2
ROUNDS_PER_USER = 2  # 100

MINIMUM_POWER = -80  # dbW

# CITY SPECIFIC PARAMETERS
# percentage of population using the network
ACTIVITY = 0.007  # 0.7%
# Average height of buildings in an area (used for RMa 5G NR only)
AVG_BUILDING_HEIGHT = 14  # current number based on average two-story building
AVG_STREET_WIDTH = 10

# BASE STATION PROPERTIES
BS_RANGE = 5000  # maximum range of base stations based on the fact that UMa and UMi models cannot exceed 5km

MCL = 70  # in dbW
HEIGHT_ABOVE_BUILDINGS = 20  # Average height a BS is above buildings (used for LTE)
CARRIER_FREQUENCY = 2000  # TODO remove?
BASE_POWER = 43  # TODO remove
G_TX = 15
G_RX = 0

CHANNEL_BANDWIDTHS = [20, 15, 10, 5, 3, 1.4]
SIGNAL_NOISE = -100

# mmWave channel properties
MMWAVE_PROBABILITY = 0
MMWAVE_FREQUENCY = 26000  # 26GHz in MHz
MMWAVE_POWER = 40
BEAMFORMING_GAIN = 30  # TODO get value
BEAMFORMING_CLEARANCE = 10  # degrees

# User equipment properties
UE_HEIGHT = 1.5  # height in meters

# RISKS ENABLED
# if a large disaster occurred, for instance a natural disaster or a depending failure
LARGE_DISASTER = True
POWER_OUTAGE = False
RADIUS_PER_SEVERITY = 1000

# malicious attacks on a certain region, for instance a DDoS
MALICIOUS_ATTACK = False
PERCENTAGE_BASE_STATIONS = 0.5
FUNCTIONALITY_DECREASED_PER_SEVERITY = 0.1

# increasing requested data
INCREASING_REQUESTED_DATA = False
OFFSET = 10
DATA_PER_SEV = 10
WINDOW_SIZE = 10
