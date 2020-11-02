#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""
"""adapted from: https://python-sounddevice.readthedocs.io/en/0.4.1/examples.html#real-time-text-mode-spectrogram"""
import argparse
import math
import shutil

import numpy as np
import sounddevice as sd

usage_line = ' press <enter> to quit, +<enter> or -<enter> to change scaling '

f = open('data.csv','w')

noise_spectrum = []
noise_thresh = 2;
alarm_types  = {
        'ALARM SPECTR': {'nsamples':10, 'thresh': {4:2}},
        'NORMAL BEEP':  {'nsamples':3,  'thresh': {6:3, 'default':-3}},
        'NO ALARM':     {'nsamples':50, 'thresh': {'default':0}}
        }

# liste the caracteristics of the alarms spectra in decreasing order of importance
# positive value in thresh: require that this bin is above ; negative value: require that this bin is below
# null value : reguire that below the noise spectrum

# types of conditions
# 1) zero, one or more bins are above a certain threshold and the others are below the noise threshold
# 2) one or more bins are above a certain theshold, and no conditions for the other bins
# instead of absolute values, use relative ones

def publish_alarm(alarm_name):

    global alarm_types
    print('-> ' + alarm_name)
    #print(alarm_types[alarm_name])

    return

def extract_alarm_type(history, buffer_size, thresh):

    a = [np.round(history[0][j],3) if history[0][j] > noise_spectrum[j] else 0 for j in range(0,20)];
    b = [str(x) if x > 0 else ''for x in a];
    if (buffer_size == 3) & (sum(a) > 0):
        print("{: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5} {: >5}".format(*b))

    L = len(history[0])
    ok = True
    for i in range(0,buffer_size):
        #print('****' + str(history[i][mybin]))

        for j in range (0, L):
            if j in thresh:
                if np.sign(thresh[j]) * history[i][j] < thresh[j]:
                    ok = False
                    break;
            elif 'default' in thresh:
                if thresh['default'] == 0:
                    if history[i][j] > noise_spectrum[j]:
                        ok = False
                        break;
                else:
                    if np.sign(thresh['default']) * history[i][j] < thresh['default']:
                        ok = False
                        break;
    return ok

def analyze_magnitude(history, magnitude, whattodo):
    global alarm_types
    global noise_spectrum

    m = np.round(np.array(magnitude),4)
    mas = ';'.join(m.astype(str)).replace('.', ',')
    #print(mas)
    f.write(mas + '\n') #Give your csv text here.

    history_length = 200 #100a

    history.insert(0,magnitude)
    if len(history) > history_length:
        history.pop()
    else:
        return history

    if whattodo== 'check_noise':
        #background noise calibration
        #should be more careful than that
        avg = np.average(history, 0)
        std = np.std(history, 0)

        coeff = 10
        noise_spectrum = np.add(avg,np.multiply(coeff,std));

        print('noise_spectrum')
        print(noise_spectrum)

    elif whattodo=='check_alarm':

        alarm_type = ''
        for alarm_name, val in alarm_types.items():
            if alarm_type == '':
                alarm_type = alarm_name if extract_alarm_type(history, val['nsamples'], val['thresh']) == True else ''
            else:
                break

        if alarm_type == '':
            #UNDETERMINED LOUD SOUND
            s = int(sum(magnitude))
            if s > 10:
                alarm_type = 'LOUD' + str(s);

        if alarm_type != '':
            publish_alarm(alarm_type)

    return history

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


try:
    columns, _ = shutil.get_terminal_size()
except AttributeError:
    columns = 80

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__ + '\n\nSupported keys:' + usage_line,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-b', '--block-duration', type=float, metavar='DURATION', default=50,
    help='block size (default %(default)s milliseconds)')
parser.add_argument(
    '-c', '--columns', type=int, default=columns,
    help='width of spectrogram')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-g', '--gain', type=float, default=10,
    help='initial gain factor (default %(default)s)')
parser.add_argument(
    '-r', '--range', type=float, nargs=2,
    metavar=('LOW', 'HIGH'), default=[100, 2000],
    help='frequency range (default %(default)s Hz)')
args = parser.parse_args(remaining)
low, high = args.range
if high <= low:
    parser.error('HIGH must be greater than LOW')

# Create a nice output gradient using ANSI escape sequences.
# Stolen from https://gist.github.com/maurisvh/df919538bcef391bc89f
colors = 30, 34, 35, 91, 93, 97
chars = ' :%#\t#%:'
gradient = []
history = []
for bg, fg in zip(colors, colors[1:]):
    for char in chars:
        if char == '\t':
            bg, fg = fg, bg
        else:
            gradient.append('\x1b[{};{}m{}'.format(fg, bg + 10, char))

try:
    samplerate = sd.query_devices(args.device, 'input')['default_samplerate']

    delta_f = (high - low) / (args.columns - 1)
    fftsize = math.ceil(samplerate / delta_f)
    low_bin = math.floor(low / delta_f)

    def callback(indata, frames, time, status):
        global history ## this should actually be passed as an argument of the callback -> need to modify the plugin too

        if status:
            return
            print(status)
            text = ' ' + str(status) + ' '
            print('\x1b[34;40m', text.center(args.columns, '#'),'\x1b[0m', sep='')
        if any(indata):
            magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
            magnitude *= args.gain / fftsize

            if len(noise_spectrum) == 0:
                history = analyze_magnitude(history, magnitude, 'check_noise')
            else:
                history = analyze_magnitude(history, magnitude, 'check_alarm')

            #it is in this magnitude that you find the data for the signatures

            line = (gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))]
                    for x in magnitude[low_bin:low_bin + args.columns])
            print(*line, sep='', end='\x1b[0m\n')
        else:
            print('no input')

    with sd.InputStream(device=args.device, channels=1, callback=callback,
                        blocksize=int(samplerate * args.block_duration / 1000),
                        samplerate=samplerate):
        while True:
            response = input()
            if response in ('', 'q', 'Q'):
                break
            for ch in response:
                if ch == '+':
                    args.gain *= 2
                elif ch == '-':
                    args.gain /= 2
                else:
                    print('\x1b[31;40m', usage_line.center(args.columns, '#'),
                          '\x1b[0m', sep='')
                    break
except KeyboardInterrupt:
    parser.exit('Interrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
