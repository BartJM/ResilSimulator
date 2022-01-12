from objects.Link import UE_BS_Link
import resilsim.objects.BaseStation as BS
import resilsim.objects.UE as UE
import resilsim.util as util
import resilsim.objects.City as City
import resilsim.settings as settings

import numpy as np


def main_test():
    channel_test()
    pass


def base_station_test():
    BS = BaseStation("LTE", 204, 8, 404, 123123, 0, 5, 52, 1000, 106, 1, 12941189449, 13842455404, 0)
    dummyUE = UserEquipment(0, 5.0001, 52.004, 20)
    pass


def channel_test():
    AMOUNT_OF_DEVICES = 25

    BS = BaseStation("LTE", 204, 8, 404, 123123, 0, 5, 52, 1000, 106, 1, 12941189449, 13842455404, 0)
    all_cap = np.random.randint(12, 50, AMOUNT_OF_DEVICES)
    dummy_lat, dummyLon = 52.11, 5.0001
    dist = distance(dummy_lat, dummyLon, 52, 5)
    print(dist)

    for i in range(AMOUNT_OF_DEVICES):
        dummyUE = UserEquipment(0, dummyLon, dummy_lat, all_cap[i])
        link = UE_BS_Link(dummyUE, BS, dist)
        BS.add_ue(link)
        dummyUE.set_base_station(link)

    BS.direct_capacities()
    print(BS)
    print(link.shannon_capacity)


def nr_model_test():
    ue = UE.UserEquipment(1,2,2,100)
    bs = BS.BaseStation(1,util.BaseStationRadioType.NR,102,102,32,City.Area(0,0,4000,4000))
    bs.add_channel(773,31)

    bs.add_ue(ue)
    power = ue.link.power
    enough = power > util.to_pwr(settings.MINIMUM_POWER)
    print(f"enough power? {enough}: {power=} with min power = {util.to_pwr(settings.MINIMUM_POWER)}")


if __name__ == '__main__':
    nr_model_test()
    #main_test()
