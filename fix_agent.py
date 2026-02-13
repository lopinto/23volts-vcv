import os
import re

def fix_midi_cpp_logic(content):
    print("   -> Aggiornamento logica driver MIDI in midi.cpp...")
    
    # In Rack 2, la gestione dei driver MIDI nei menu è diversa.
    # Invece di iterare manualmente gli ID, usiamo gli helper moderni o adattiamo la chiamata.
    
    # ERRORE 1: port->getDriverIds() non esiste più.
    # In Rack 2 si usa midi::getDriverIds() globale, oppure port->getDriverId() per quello corrente.
    # Ma qui stiamo costruendo un MENU, quindi vogliamo la lista.
    # La soluzione rapida è usare la funzione globale di Rack.
    
    if "port->getDriverIds()" in content:
        content = content.replace("port->getDriverIds()", "rack::midi::getDriverIds()")

    # ERRORE 2: port->getDriverName(driverId) -> rack::midi::getDriverName(driverId)
    if "port->getDriverName(driverId)" in content:
        content = content.replace("port->getDriverName(driverId)", "rack::midi::getDriverName(driverId)")

    return content

def main():
    print("🤖 AGENTE 23VOLTS: Fix Menu MIDI...")
    
    path = "src/common/midi.cpp"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            original = f.read()
        
        content = fix_midi_cpp_logic(original)

        if content != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"🔧 Riparato: {path}")
        else:
            print(f"⚠️ Nessuna modifica su {path}. Controlla se il codice è già aggiornato.")
    else:
        print(f"❌ Errore: {path} non trovato!")

    print("\n✅ Fix driver applicato. Esegui git push.")

if __name__ == "__main__":
    main()
