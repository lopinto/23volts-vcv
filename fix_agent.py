import os

def fix_midi_cpp_final():
    path = "src/common/midi.cpp"
    print(f"🔎 Controllo file: {path}...")
    
    if not os.path.exists(path):
        print(f"❌ Errore: {path} non trovato!")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # FIX: rack::midi::getDriverName(id) non esiste. 
    # Bisogna prima ottenere il puntatore al driver e poi chiamare getName().
    
    bad_code = "rack::midi::getDriverName(driverId)"
    good_code = "rack::midi::getDriver(driverId)->getName()"
    
    if bad_code in content:
        print("   -> Correggo la chiamata al driver MIDI...")
        content = content.replace(bad_code, good_code)

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ File {path} salvato con le correzioni.")
    else:
        print(f"⚠️ Nessuna modifica necessaria. Forse è già stato corretto?")

if __name__ == "__main__":
    fix_midi_cpp_final()
