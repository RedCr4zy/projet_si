from pyo import *

NOTE_TO_FREQ = {
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "G4": 392.00,
    "A4": 440.00,
}

# === Configuration du serveur audio ===
s = Server(duplex=0, sr=44100)  # duplex=0 pour sortie seulement
s.setOutputDevice(5)             # <- Remplace par l’index qui marche pour toi
s.boot()
s.start()
print("Serveur pyo démarré sur le périphérique correct")

# === Fonctions de son ===
def piano(freq, dur=1.5, amp=0.4):
    osc = Sine(freq=freq, mul=amp)
    env = Adsr(0.005, 0.15, 0.4, 0.3, dur=dur)
    (osc * env).out()
    env.play()

def synth(freq, dur=0.5, amp=0.3):
    osc = LFO(freq=freq, type=2, mul=amp)
    env = Adsr(0.02, 0.1, 0.7, 0.4, dur=dur)
    Freeverb(osc * env, size=0.8).out()
    env.play()

def play_beep(freq=440, dur=0.3, amp=0.4):
    osc = Sine(freq=freq, mul=amp)
    env = Adsr(attack=0.01, decay=0.1, sustain=0.6, release=0.2, dur=dur)
    (osc * env).out()
    env.play()

# === Test rapide ===
play_beep()
print("Instrument de test joué")
input("Appuyez sur Entrée une fois que vous avez entendu le son...\n")
