import serial

class DlmsError(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return repr(self.reason)

class Dlms():
    def __init__(self, port, baudrate=9600, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, timeout=10):
        self.ser = serial.Serial(port=port, baudrate=baudrate, bytesize=bytesize, parity=parity, timeout=timeout)

    def query(self):
        self.ser.write(b'/?!\r\n')
        state = 0
        id = ""
        cont = ""
        sum = 0
        while True:
            a = self.ser.read(1)
            if len(a) == 0:
                raise DlmsError("Rx Timeout")
            b = bytearray(a)[0]
            if state == 0:
                # Read ID string 
                if b >= 32:
                    id += a.decode()
                elif b == 13:
                    state = 1
                else:
                    raise DlmsError("Illegal char in ident 0x%02x" % b)
                    state = 99
            elif state == 1:
                # NL ending ID string
                if b != 10:
                    raise DlmsError("Ident has 0x%02x after CR" % b)
                    state = 99
                else:
                    state = 2
            elif state == 2:
                # STX
                if b != 2:
                    raise DlmsError("Expected STX not 0x%02x" % b)
                    state = 99
                else:
                    state = 3
            elif state == 3:
                # message body
                sum ^= b
                if b != 3:
                    cont += a.decode()
                else:
                    state = 4
            elif state == 4:
                # Checksum
                if sum != b:
                    raise DlmsError("Checksum Mismatch")
                    state == 99
                else:
                    return self.parse(id, cont)
            elif state == 99:
                # Error, flush
                pass
        assert False

    def parse(self, id, cont):
        l = list()
        l.append(id)
        l.append(dict())
        cont = cont.split("\r\n")
        if cont[-1] != "":
            raise DlmsError("Last data item lacks CRNL")
        if cont[-2] != "!":
            raise DlmsError("Last data item not '!'")
        for i in cont[:-2]:
            if i[-1] != ")":
                raise DlmsError("Last char of data item not ')'")
                return None
            i = i[:-1].split("(")
            j = i[1].split("*")
            l[1][i[0]] = j
        return l
