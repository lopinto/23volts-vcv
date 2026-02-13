import os
import re

def fix_header_files(content):
    # 1. Aggiunge <deque> se manca in midi.hpp
    if "struct MidiInput" in content and "#include <deque>" not in content:
        content = "#include <deque>\n" + content

    # 2. DEFINIZIONE DEL "MAGAZZINO" (La coda manuale)
    # Iniettiamo std::deque direttamente nelle struct
    queue_decl = " std::deque<rack::midi::Message> messageQueue; "
    # Funzione shift manuale (solo per Input e InputOutput)
    shift_func = " bool shift(rack::midi::Message *msg) { if (messageQueue.empty()) return false; *msg = messageQueue.front(); messageQueue.pop_front(); return true; } "

    # 3. FIX MidiInput e MidiInputOutput (Coda + Shift)
    # Cerchiamo la definizione della struct e iniettiamo il codice
    content = re.sub(
        r'(struct\s+MidiInput\s*:\s*(?:rack::)?midi::Input\s*\{)', 
        r'\1' + queue_decl + shift_func, 
        content
    )
    content = re.sub(
        r'(struct\s+MidiInputOutput\s*:\s*(?:rack::)?midi::Input\s*\{)', 
        r'\1' + queue_decl + shift_func, 
        content
    )

    # 4. FIX MidiOutput (Solo Coda) - IL FIX CHE MANCAVA PRIMA
    # Anche se MidiOutput non usa shift, onMessage prova a scriverci dentro.
    # Quindi DEVE avere messageQueue.
    if "struct MidiOutput" in content and "messageQueue;" not in content:
        content = re.sub(
            r'(struct\s+MidiOutput\s*:\s*(?:rack::)?midi::Output\s*\{)', 
            r'\1' + queue_decl, 
            content
        )

    return content

def fix_source_files(content):
    # Fix per API VCV Rack 2 (Porte, Label, Menu)
    replacements = [
        (r'\bINPUT\b', 'rack::engine::Port::INPUT'),
        (r'\bOUTPUT\b', 'rack::engine::Port::OUTPUT'),
        (r'\bMenuLabel\b', 'rack::ui::MenuLabel'),
        (r'\bLabel\b', 'rack::app::Label'),
        (r'paramQuantity->', 'getParamQuantity()->'),
        (r'delete cells;', 'delete[] cells;'),
        (r'std::auto_ptr', 'std::unique_ptr'),
    ]
    
    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    # Fix onMessage: Firma e Logica
    if "onMessage" in content:
        # 1. Cambia firma (aggiunge const e &)
        content = content.replace(
            "onMessage(rack::midi::Message message)", 
            "onMessage(const rack::midi::Message& message)"
        )
        # 2. Inietta il push nella coda all'inizio della funzione
        # Cerca la definizione della funzione e aggiunge l'istruzione push_back
        content = re.sub(
            r'(onMessage\(const rack::midi::Message& message\) override\s*\{)', 
            r'\1 messageQueue.push_back(message);', 
            content
        )

    return content

def main():
    print("🤖 AGENTE 23VOLTS: Avvio riparazione su codice pulito...")
    
    modified_files = 0
    # Scansiona cartella src
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith((".hpp", ".cpp")):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        original = f.read()
                    
                    content = original
                    
                    # Applica logica specifica per header o cpp
                    if file.endswith(".hpp"):
                        content = fix_header_files(content)
                    
                    content = fix_source_files(content)

                    if content != original:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"🔧 Riparato: {file}")
                        modified_files += 1
                except Exception as e:
                    print(f"Errore su {file}: {e}")

    print(f"\n✨ {modified_files} file corretti e pronti per il push!")

if __name__ == "__main__":
    main()
