from pySerialTransfer import pySerialTransfer as txfer
import time

class pressureCodes(object):
    pressureCode1 = 0
    pressureCode2 = 0

class sensors(object):
    flowchan1 = 0
    flowchan2 = 0
    pressuresensor1 = 0
    pressuresensor2 = 0

def write_read(link, TX, RX):
    sendSize, recSize = 0, 0
    sendSize = link.tx_obj(TX.pressureCode1, sendSize)
    link.send(sendSize)  # send value to Arduino

    while not link.available():  # wait until we get a value from Arduino
        if link.status < 0:
            if link.status == txfer.CRC_ERROR:
                print('ERROR: CRC_ERROR')
            elif link.status == txfer.PAYLOAD_ERROR:
                print('ERROR: PAYLOAD_ERROR')
            elif link.status == txfer.STOP_BYTE_ERROR:
                print('ERROR: STOP_BYTE_ERROR')
            else:
                print('ERROR: {}'.format(link.status))

    RX.flowchan1 = link.rx_obj(obj_type=float, start_pos=recSize)  # read response from Arduino
    recSize += txfer.STRUCT_FORMAT_LENGTHS['f']
    RX.pressuresensor1 = link.rx_obj(obj_type=int, start_pos=recSize)

def main():
    # write pressure to arduino, and read flow rate back
    TX = pressureCodes
    RX = sensors
    link = txfer.SerialTransfer('COM14')  #Change this to the right COM port
    link.open()
    time.sleep(2) # allow some time for the Arduino to completely reset
    print('Connected to device')
    count = 0
    while True:
        if count%100==0:
            TX.pressureCode1+=50
        count+=1
        write_read(link, TX, RX)
        print('sent: {} | received: f:{} p:{}'.format(TX.pressureCode1, RX.flowchan1, RX.pressuresensor1))
        #print(count)
if __name__ == '__main__':
    main()
