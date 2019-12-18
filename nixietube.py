import pyb
from pyb import Pin

FONT = {
    '0': 0x00,
    '1': 0x01,
    '2': 0x02,
    '3': 0x03,
    '4': 0x04,
    '5': 0x05,
    '6': 0x06,
    '7': 0x07,
    '8': 0x08,
    '9': 0x09,
    '-': 0x0a,
    'E': 0x0b,
    'H': 0x0c,
    'L': 0x0d,
    'P': 0x0e,
    ' ': 0x0f
}

class NixieTube(object):
    """Nixie Tube

        The rotational displacement is converted into a series of digital pulses,
        which are then used to control the angular displacement

    Attributes:
        clk: pin of the clk connected
        cs: pin of the cs connected
        din: pin of the din connected
        digit_count: the number of "8" on the nixie tube
    """
    
    def __init__(self, clk, cs, din, digit_count):
        super(NixieTube, self).__init__()
        
        self.clk = Pin(clk, Pin.OUT_PP)
        self.cs = Pin(cs, Pin.OUT_PP)
        self.din = Pin(din, Pin.OUT_PP)
        
        self.digit_count = digit_count
        
        self.reset()
    
    def reset(self):
        """reset the nixie tube

            Enter the working state and display blank
        """
        # set Decode Mode
        self.__write_data(0x09, self.__get_decode_mode())
        # set Intensity
        self.__write_data(0x0a, 0x03)
        # set Scan Limit, The scan-limit register sets how many digits are displayed, from 1 to 8
        self.__write_data(0x0b, self.digit_count - 1)
        # set Shutdown:Shutdown Mode 0, Normal Operation: 1
        self.__write_data(0x0c, 0x01)
        # set Display Test:Normal Operation 0, Display Test Mode: 1
        self.__write_data(0x0f, 0x00)
        
        # set all digits to blank
        for index in range(self.digit_count):
            self.display_char(index, ' ')
    
    def display_char(self, index, char, show_dp=False):
        """Specifies the index location display character
        
        Args:
            index: the index location where want to show character
            char: the character want to show, must in FONT
            show_dp: whether to display the decimal point
        """
        if index >= self.digit_count:
            return
        if not(char in FONT):
            print('no chat find')
            return
        data = FONT[char]
        self.__write_data(index + 1, (data|0x80) if (show_dp) else data)
    
    def off(self):
        """set the nixie tube to shutdown mode
        """
        self.__write_data(0x0c, 0x00)
    
    def test(self):
        """set the nixie tube to display test mode
        """
        self.__write_data(0x0f, 0x01)
    
    def __write_data(self, addr, data):
        """write data to nixie tube
        
        Args:
            addr: the Register address, corresponding to the index location
            data: the data want to write to nixie tube
        """
        self.cs.value(0)
        self.__write_byte(addr)
        self.__write_byte(data)
        self.cs.value(1)
        pyb.udelay(1)
    
    def __write_byte(self, data):
        """write data to nixie tube
        
        Args:
            data: the data want to write to nixie tube
        """
        for i in range(8):
            self.clk.value(0)
            self.din.value(data&0x80)
            data <<= 1
            self.clk.value(1)
    
    def __get_decode_mode(self):
        """Return decode_mode based on the number of digit
        
        Returns:
            decode_mode: which mode the decode mode register to use
        """
        if self.digit_count == 1:
            return 0x01
        elif self.digit_count == 4:
            return 0x0f
        else:
            return 0xff
