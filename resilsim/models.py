import numpy as np
import math

import resilsim.util as util
import resilsim.settings as settings
import resilsim.objects.BaseStation as bso


def pathloss(radio, distance):
    # For 5G NR (and mmWave)
    if radio is bso.BaseStationRadioType.NR or radio is bso.BaseStationRadioType.mmWave:
        pass
    # For LTE
    elif radio is bso.BaseStationRadioType.LTE:
        MODEL_A = -18 * np.log10(settings.HEIGHT_ABOVE_BUILDINGS) + 21 * np.log10(settings.CARRIER_FREQUENCY) + 80
        MODEL_B = 40 * (1 - 4 * (10 ** -3) * settings.HEIGHT_ABOVE_BUILDINGS)
        return (MODEL_A + MODEL_B * math.log10(distance / 1000)) + math.sqrt(10) * np.random.random()


def shannon_capacity(bandwidth, tx, distance):
    return bandwidth * second_param_capacity(tx, distance)


def second_param_capacity(tx, distance):
    return math.log2(1 + snr(tx, distance))


def snr(tx, distance):
    return received_power(tx, distance) / util.to_pwr(settings.SIGNAL_NOISE)


def received_power(tx, distance):
    # TODO change G_TX and G_RX to go through beamforming model (if needed)
    return util.to_pwr(tx - max(pathloss(distance) - settings.G_TX - settings.G_RX, settings.MCL))
