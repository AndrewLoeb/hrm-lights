#import bluetooth #pybluez
import dbus #python3-dbus
from pprint import pprint
from time import sleep


def dbus_to_python(data):
    """convert D-Bus data types to python data types"""
    if isinstance(data, dbus.String):
        data = str(data)
    elif isinstance(data, dbus.Boolean):
        data = bool(data)
    elif isinstance(data, dbus.Byte):
        data = int(data)
    elif isinstance(data, dbus.UInt16):
        data = int(data)
    elif isinstance(data, dbus.UInt32):
        data = int(data)
    elif isinstance(data, dbus.Int64):
        data = int(data)
    elif isinstance(data, dbus.Double):
        data = float(data)
    elif isinstance(data, dbus.ObjectPath):
        data = str(data)
    elif isinstance(data, dbus.Array):
        if data.signature == dbus.Signature('y'):
            data = bytearray(data)
        else:
            data = [dbus_to_python(value) for value in data]
    elif isinstance(data, dbus.Dictionary):
        new_data = dict()
        for key in data:
            new_data[dbus_to_python(key)] = dbus_to_python(data[key])
        data = new_data
    return data


def get_managed_objects(bus):
    """
    Return the objects currently managed by the D-Bus Object Manager for BlueZ.
    """
    BLUEZ_SERVICE_NAME = "org.bluez"
    manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, "/"),
        "org.freedesktop.DBus.ObjectManager"
    )
    return manager.GetManagedObjects()


def gatt_chrc_path(bus, uuid, path_start="/"):
    """
    Find the D-Bus path for a GATT Characteristic of given uuid.
    Use `path_start` to ensure it is on the correct device or service
    """
    BLUEZ_GATT_CHRC = "org.bluez.GattCharacteristic1"
    for path, info in get_managed_objects(bus).items():
        found_uuid = info.get(BLUEZ_GATT_CHRC, {}).get("UUID", "")
        if all((uuid.casefold() == found_uuid.casefold(),
                path.startswith(path_start))):       
            return path
    return None


class BluezProxy(dbus.proxies.Interface):
    """
        A proxy to the remote Object. A ProxyObject is provided so functions
        can be called like normal Python objects.
     """
    def __init__(self, bus, dbus_path, interface):
        BLUEZ_SERVICE_NAME = "org.bluez"
        self.dbus_object = bus.get_object(BLUEZ_SERVICE_NAME, dbus_path)
        self.prop_iface = dbus.Interface(self.dbus_object,
                                         dbus.PROPERTIES_IFACE)
        super().__init__(self.dbus_object, interface)

    def get_all(self):
        """Return all properties on Interface"""
        return dbus_to_python(self.prop_iface.GetAll(self.dbus_interface))

    def get(self, prop_name, default=None):
        """Access properties on the interface"""
        try:
            value = self.prop_iface.Get(self.dbus_interface, prop_name)
        except dbus.exceptions.DBusException:
            return default
        return dbus_to_python(value)

class polarHRM():
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

        self.BLUEZ_SERVICE_NAME = "org.bluez"
        self.BLUEZ_ADAPTER = "org.bluez.Adapter1"
        self.BLUEZ_DEVICE = "org.bluez.Device1"
        self.BLUEZ_GATT_CHRC = "org.bluez.GattCharacteristic1"
        self.ADAPTER_PATH = "/org/bluez/hci0"
        self.DEVICE_ADDR = "A0:9E:1A:A9:D9:89"
        self.DEVICE_PATH = f"{self.ADAPTER_PATH}/dev_{self.DEVICE_ADDR.replace(':', '_')}"
        self.dongle = BluezProxy(self.bus, self.ADAPTER_PATH, self.BLUEZ_ADAPTER)
        self.device = BluezProxy(self.bus, self.DEVICE_PATH, self.BLUEZ_DEVICE)

    def ConnectToHR(self):
        if self.device.get("Connected"):
            print("Already Connected")
        else:
            while True:
                print("Trying to connect...")
                try:
                    self.device.Connect()
                    break
                except dbus.exceptions.DBusException:
                    sleep(1)
            print("Connected")
            while not self.device.get("ServicesResolved"):
                print("Trying to resolve services...")
                sleep(0.5)
        self.tmp_val_path = gatt_chrc_path(self.bus, self.HR_UUID, self.device.object_path)
        self.tmp_chrc = BluezProxy(self.bus, self.tmp_val_path, self.BLUEZ_GATT_CHRC)  
        self.tmp_chrc.StartNotify()

    def readHR(self):
        if not self.device.get("Connected"):
            return None
        else:
            hrValue = bytes(self.tmp_chrc.get("Value"))[1]
            return hrValue
            
    def DisconnectToHR(self):
        # Disconnect from device
        self.device.Disconnect()
