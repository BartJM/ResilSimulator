from resilsim.settings import OPEN_CHANNELS, CHANNEL_BANDWIDTHS, BASE_POWER
from resilsim.objects.Link import BS_BS_Link, BS_UE_Link
import math
import random
import enum


@enum.unique
class BaseStationRadioType(enum.Enum):
    NR = enum.auto()
    LTE = enum.auto()
    mmWave = enum.auto()


class BaseStation:
    def __init__(self, radio: BaseStationRadioType, lon, lat):
        self.radio = radio
        self.lon = float(lon)
        self.lat = float(lat)

        self.connected_UE_links = list()
        self.connected_UE = list()
        self.connected_BS = list()

        self.minimum_band_needed = dict()

        self.channels = list()
        self.functional = 1

    def __str__(self):
        startmsg = "Base station[], lon:{}, lat:{}, radio:{}".format(self.lon, self.lat,
                                                                     self.radio)
        for channel in self.channels:
            startmsg += "\n{}".format(str(channel))
        return startmsg

    def malfunction(self, new_functional):
        self.functional = new_functional
        self.create_new_channels()

    def add_link(self, link: BS_BS_Link):
        self.connected_BS.append(link)

    def add_channel(self, frequency, power):
        """
        Adds an omnidirectional channel to the basestation
        :param frequency: The frequency of the channel
        :param power: The transmit power for this channel
        :return: None
        """
        # Check if channel exist already
        for c in self.channels:
            if c.frequency == frequency:
                return
        channel = Channel(frequency, power)
        self.channels.append(channel)

    def __add__(self, other):
        new_link = BS_BS_Link(self, other)
        self.connected_BS.append(new_link)
        other.add_link(new_link)
        return new_link

    def add_ue(self, link: BS_UE_Link):
        self.connected_UE_links.append(link)
        self.connected_UE.append(link.ue)

        if link.bandwidthneeded not in self.minimum_band_needed:
            self.minimum_band_needed[link.bandwidthneeded] = list()

        self.minimum_band_needed[link.bandwidthneeded].append(link.ue)
        channel = max(self.channels, key=lambda c: (c.productivity, c.band_left))
        channel.add_devices(link.ue, link.bandwidthneeded)

    def direct_capacities(self):
        self.create_new_channels()
        self.connected_UE = sorted(self.connected_UE, key=lambda x: x.link.bandwidthneeded, reverse=True)
        for UE in self.connected_UE:
            channel = max(self.channels, key=lambda c: (c.productivity, c.band_left))
            channel.add_devices(UE, UE.link.bandwidthneeded)

    @property
    def overflow(self):
        for UE in self.connected_UE:
            if self.get_bandwidth(UE) == 0:
                return True

        return False

    def remove_ue(self, ue_link):
        self.connected_UE_links.remove(ue_link)
        self.connected_UE.remove(ue_link.ue)

    def get_bandwidth(self, ue):
        for channel in self.channels:
            bandwidth = channel.get_bandwidth(ue)
            if bandwidth is not None:
                return bandwidth
        return 0

    def create_new_channels(self):
        """
        Changes channels based on the functionality of the basestation.
        :return:
        """
        for channel in self.channels:
            if random.random() >= self.functional:
                channel.reset()
                channel.enabled = False

    def reset(self):
        self.functional = 1
        self.create_new_channels()
        self.connected_UE.clear()
        self.connected_UE_links.clear()

    # TODO add channels (and ue links?) to the copy
    def get_copy(self):
        return BaseStation(self.radio, self.lon, self.lat)


class Channel:
    def __init__(self, frequency, power, enabled=True):
        self.frequency = frequency
        self.power = power

        self.devices = dict()
        self.desired_band = dict()

        self.enabled = enabled

        a = [20, 15, 10, 5, 3, 1.3]
        d1 = 12

    def add_devices(self, ue, minimum_bandwidth):
        self.devices[ue] = minimum_bandwidth
        self.desired_band[ue] = minimum_bandwidth

        while self.band_left < 0:
            device = max(self.devices, key=lambda d: self.devices[d])
            stop_next = False
            for i in CHANNEL_BANDWIDTHS:
                if stop_next:
                    stop_next = False
                    break

                if self.devices[device] == i:
                    stop_next = True

            if stop_next:
                self.devices[device] = 0
                break

            self.devices[device] = i

    @property
    def band_left(self):
        return CHANNEL_BANDWIDTHS[0] - sum([self.devices[d] for d in self.devices])

    @property
    def connected_devices(self):
        return len(self.devices)

    @property
    def productivity(self):
        if len(self.devices) == 0:
            return 1
        return sum(self.devices.values()) / sum(self.desired_band.values())

    def __str__(self):
        msg = "Channel[{}]:".format(self.frequency)
        for device in self.devices:
            msg += "\n{} Desired Bandwidth:{}, Actual Bandwidth:{}".format(device, self.desired_band[device],
                                                                           self.devices[device])
        return msg

    def __eq__(self, other):
        if not isinstance(other, Channel):
            raise TypeError
        return self.frequency == other.frequency

    def get_bandwidth(self, ue):
        if ue not in self.devices:
            return None

        return self.devices[ue]

    def reset(self):
        self.devices.clear()
        self.desired_band.clear()
