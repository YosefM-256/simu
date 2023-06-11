import pytesseract
import PIL
import pyautogui
import cv2 as cv
import time
import numpy as np

global segments; segments = \
           {"Vout_dac":(469,491,668,525),\
            "Vb_dut":(735,475,927,506),\
            "Ib_dut":(735,506,931,544)}

global dac_state; dac_state = 0
dac_keys = ['q','w','e','r','t','y','u','i','o','p','j','k']
delay_after_press = 50 # in milliseconds
path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

pytesseract.tesseract_cmd = path

def screen_capture():
    '''captures a screenshot. returns an image object'''
    return pyautogui.screenshot()

def break_image(image, segments):
    '''takes an image object and a list of segments and breaks it into several images.
each segment is a tuple that goes (x0,y0,x1,y1)'''
    return [image.crop(seg) for seg in segments]

def image_into_text(image):
    '''takes an image object and returns the text using tesseract'''
    pytesseract.image_to_string(image)

def image_to_numpy(image):
    '''takes an image object and returns a numpy array of the image'''
    im = np.array(image);
    im_copy = im.copy(); im[:,:,0] = im_copy[:,:,2]; im[:,:,2] = im_copy[:,:,0];
    return im

def text_to_num(text):
    '''takes the text the function "pytesseract.image_to_string" returns
and returns it as a "double" type number'''
    const = {'m': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12}
    text = text.strip('\n')
    multip = text[-2]
    if not(multip in const):
        raise ValueError("an unknown constant was given: " + multip + \
                         " with the text: " + text)
    num = float(text[3:-4])*const[multip]
    return num

def data_capture():
    '''takes no arguments and returns a dictionary of the data it reads
from the screen'''
    global segments
    data = {}
    screen = screen_capture()
    for seg in segments:
        text = pytesseract.image_to_string(screen.crop(segments[seg]))
        data[seg] = text_to_num(text)
    return data

def dac_state_bin():
    '''returns a string that represents the binary state of the dac'''
    global dac_state; state = dac_state
    bin_state = bin(state)[2:]
    bin_state = '0'*(12 - len(bin_state)) + bin_state
    return bin_state

def state_bin(state):
    '''returns a string that represents the binary state of the given state'''
    bin_state = bin(state)[2:]
    bin_state = '0'*(12 - len(bin_state)) + bin_state
    return bin_state

def key_press(index):
    global dac_state
    dac_bin_state = dac_state_bin()
    pyautogui.press(dac_keys[index])
    dac_state += ( 2**(11-index) )*(1 if not(int(dac_bin_state[index])) else -1)
    
def change_dac(state):
    '''takes a desired dac state as an integer and changes the dac to achieve it'''
    req_bin_state = state_bin(state)
    dac_bin_state = dac_state_bin()
    global dac_state
    print('req_bin_state:', req_bin_state, 'dac_bin_state:', dac_bin_state)
    for i in range(12):
        if dac_bin_state[i] != req_bin_state[i]:
            key_press(i)
            print("pressed ", dac_keys[i], "index:", i, "dac_state:", dac_state)
            time.sleep(0.001*delay_after_press)

time.sleep(5)
change_dac(3)
print("hey ho here we go")
change_dac(0)
print("either a little to high or a little to low")
aquired_data = []
for i in range(0,500,5):
    change_dac(i)
    time.sleep(1)
    aquired_data.append(data_capture())
    print(i)
    time.sleep(1)
while True:
    '''
    im = screen_capture().crop(segments["Vout_dac"])
    text = pytesseract.image_to_string(im)
    print(text[:-1])
    cv.imshow('',image_to_numpy(im))
    '''
    cv.waitKey(1000)
    print(data_capture())


