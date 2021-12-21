from objects.Link import BS_UE_Link
from resilsim.objects.BaseStation import BaseStation
from resilsim.objects.UE import UserEquipment
from resilsim.util import distance

import numpy as np

def main_test():
    channel_test()
    pass


def base_station_test():
    BS = BaseStation("LTE",204,8,404,123123,0,5,52,1000,106,1,12941189449,13842455404,0)
    dummyUE = UserEquipment(0,5.0001,52.004,20)
    pass


def channel_test():
    AMOUNT_OF_DEVICES = 25

    BS = BaseStation("LTE", 204, 8, 404, 123123, 0, 5, 52, 1000, 106, 1, 12941189449, 13842455404, 0)
    all_cap = np.random.randint(12,50,AMOUNT_OF_DEVICES)
    dummy_lat, dummyLon = 52.11,5.0001
    dist = distance(dummy_lat,dummyLon,52,5)
    print(dist)

    for i in range(AMOUNT_OF_DEVICES):
        dummyUE = UserEquipment(0,dummyLon,dummy_lat,all_cap[i])
        link = BS_UE_Link(dummyUE,BS,dist)
        BS.add_ue(link)
        dummyUE.set_base_station(link)


    BS.direct_capacities()
    print(BS)
    print(link.shannon_capacity)




if __name__ == '__main__':
    main_test()
