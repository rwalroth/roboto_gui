from threading import Thread, Event
from serial.serialutil import SerialException, PortNotOpenError, SerialTimeoutException


OpCodes2Text = {
    0X11: "ABORT_MACRO_PDF",
    0XC4: "AIM_OFF",
    0XC5: "AIM_ON",
    0XD6: "BATCH_DATA",
    0XD5: "BATCH_REQUEST",
    0xE6: "BEEP",
    0xD3: "CAPABILITIES_REQUEST",
    0xD4: "CAPABILITIES_REPLY",
    0xC9: "CHANGE_ALL_CODE_TYPES",
    0xD0: "CMD_ACK",
    0xD8: "CMD_ACK_ACTION",
    0xD1: "CMD_NAK",
    0x12: "CUSTOM_DEFAULTS",
    0xF3: "DECODE_DATA",
    0xF6: "EVENT",
    0x10: "FLUSH_MACRO_PDF",
    0xD2: "FLUSH_QUEUE",
    0xC0: "ILLUMINATION_OFF",
    0xC1: "ILLUMINATION_ON",
    0xB1: "IMAGE_DATA",
    0xF7: "IMAGER_MODE",
    0xE8: "LED_OFF",
    0xE7: "LED_ON",
    0xCA: "PAGER_MOTOR_ACTIVATION",
    0xC8: "PARAM_DEFAULTS",
    0xC7: "PARAM_REQUEST",
    0xC6: "PARAM_SEND",
    0xA4: "REPLY_REVISION",
    0xA3: "REQUEST_REVISION",
    0xEA: "SCAN_DISABLE",
    0xE9: "SCAN_ENABLE",
    0xEB: "SLEEP",
    0x80: "SSI_MGMT_COMMAND",
    0xE4: "START_SESSION",
    0xE5: "STOP_SESSION",
    0xB4: "VIDEO_DATA",
}

OpCodesText2Int = {val: key for key, val in OpCodes2Text.items()}

ABORT_MACRO_PDF = 0X11
AIM_OFF = 0XC4
AIM_ON = 0XC5
BATCH_DATA = 0XD6
BATCH_REQUEST = 0XD5
BEEP = 0xE6
CAPABILITIES_REQUEST = 0xD3
CAPABILITIES_REPLY = 0xD4
CHANGE_ALL_CODE_TYPES = 0xC9
CMD_ACK = 0xD0
CMD_ACK_ACTION = 0xD8
CMD_NAK = 0xD1
CUSTOM_DEFAULTS = 0x12
DECODE_DATA = 0xF3
EVENT = 0xF6
FLUSH_MACRO_PDF = 0x10
FLUSH_QUEUE = 0xD2
ILLUMINATION_OFF = 0xC0
ILLUMINATION_ON = 0xC1
IMAGE_DATA = 0xB1
IMAGER_MODE = 0xF7
LED_OFF = 0xE8
LED_ON = 0xE7
PAGER_MOTOR_ACTIVATION = 0xCA
PARAM_DEFAULTS = 0xC8
PARAM_REQUEST = 0xC7
PARAM_SEND = 0xC6
REPLY_REVISION = 0xA4
REQUEST_REVISION = 0xA3
SCAN_DISABLE = 0xEA
SCAN_ENABLE = 0xE9
SLEEP = 0xEB
SSI_MGMT_COMMAND = 0x80
START_SESSION = 0xE4
STOP_SESSION = 0xE5
VIDEO_DATA = 0xB4


def calculate_checksum(message):
    check = 0
    for x in message:
        check += x
        check = check & 0xffff
    check2 = 0xffff - check + 1
    high = check2 >> 8
    low = check2 & 0xff
    return [high, low]


def generate_byte_message(opcode, data, source=0x04, status=0b00000000):
    """

    Parameters
    ----------
    opcode : int
    data : list of int
    source : int
    status : int

    Returns
    -------
    bytes
        Formatted message in bytes
    """
    if type(data) == int:
        ldata = [data]
    elif type(data) == list:
        ldata = data
    else:
        ldata = list(data)
    if not all(isinstance(x, int) for x in ldata):
        raise TypeError("data must be of type int or iterable of ints")
    message = [0, opcode, source, status] + ldata
    message[0] = len(message)
    message += calculate_checksum(message)
    return bytes(message)


def send_scanner_message(scanner, opcode, data, source=0x04, status=0b00000000):
    """
    Sends a message to scanner. This function does no error
    handling for closed or otherwise inaccessible scanners

    Parameters
    ----------
    scanner : serial.Serial
    opcode : int
    data : list of int
    source : int
    status : int

    Returns
    -------
    reply : int
        Length of scanner reply
    """
    message = generate_byte_message(opcode, data, source, status)
    return scanner.write(message)


def read_scanner_message(scanner):
    """
    Reads and returns raw byte message from scanner.
    This function does no error handling for closed or
    otherwise inaccessible scanners

    Parameters
    ----------
    scanner : serial.Serial

    Returns
    -------
    messageBytes : bytes
    """
    messageBytes = scanner.read(1)
    if messageBytes:
        messageLength = int.from_bytes(messageBytes, "big")
        messageBytes += scanner.read(messageLength + 1)
        if messageBytes[1] not in [CMD_ACK, CMD_NAK, CMD_ACK_ACTION]:
            send_scanner_message(scanner, CMD_ACK, [])
        print(messageBytes.hex())
        return messageBytes
    else:
        return b''


def format_scanner_reply(message):
    mLength = message[0]
    opcode = message[1]
    return {
        "length": mLength,
        "opcode": opcode,
        "optext": OpCodes2Text.get(opcode, "NOT_FOUND"),
        "source": message[2],
        "status": message[3],
        "data": message[4:mLength],
        "checksum": list(message[mLength:]),
    }


class ScannerThread(Thread):
    def __init__(self, scanner, buffer, scannerLive, *args, **kwargs):
        """

        Parameters
        ----------
        scanner : serial.Serial
        buffer : queue.Queue
        scannerLive : threading.Event
        args : list
        kwargs : dict
        """
        super(ScannerThread, self).__init__(*args, **kwargs)
        self.scanner = scanner
        self.scannerLive = scannerLive
        self.buffer = buffer
        self.exit_event = Event()

    def run(self):
        while not self.exit_event.is_set():
            if self.scannerLive.is_set():
                try:
                    message = read_scanner_message(self.scanner)
                    if message:
                        self.buffer.put(message)
                except (SerialException, PortNotOpenError,
                        SerialTimeoutException, TypeError):
                    self.scannerLive.clear()
            else:
                self.scannerLive.wait()
