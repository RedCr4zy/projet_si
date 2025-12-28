from pyo import *

NOTE_TO_FREQ = {
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "G4": 392.00,
    "A4": 440.00,
}

s = Server().boot()
s.start()

def piano(freq, dur=1.5, amp=2.3):
    osc = Sine(freq=freq, mul=amp)
    env = Adsr(0.005, 0.15, 0.4, 0.3, dur=dur)
    (osc * env).out()
    env.play()

def synth(freq, dur=0.5, amp=0.3):
    osc = LFO(freq=freq, type=2, mul=amp)
    env = Adsr(0.02, 0.1, 0.7, 0.4, dur=dur)
    Freeverb(osc * env, size=0.8).out()
    env.play()

piano(NOTE_TO_FREQ["C4"], 1)
synth(NOTE_TO_FREQ["D4"], 1)
