import os
import re

def fix_header_files(content):
    print("   -> Analisi midi.hpp...")
    
    # 1. Aggiunge <deque> se manca
    if "#include <deque>" not in content:
        content = "#include <deque>\n" + content

    # Definizioni da iniettare
    # Coda + Funzione Shift (per Input)
    injection_input = " \nstd::deque<rack::midi::Message> messageQueue; \nbool shift(rack::midi::Message *msg) { if (messageQueue.empty()) return false; *msg = messageQueue.front(); messageQueue.pop_front(); return true; } \n"
    # Solo Coda (per Output)
    injection_output = " \nstd::deque<rack::midi::Message> messageQueue; \n"

    # 2. INIEZIONE "BRUTE FORCE"
    # Cerca "struct MidiInput ... {" (ignorando cosa c'è in mezzo) e inietta subito dopo la graffa
    
    # Fix MidiInput
    if "bool shift" not in content: # Evita doppi inserimenti
        content = re.sub(
            r'(struct\s+MidiInput[^\{]*\{)', 
            r'\1' + injection_input, 
            content
        )

    # Fix MidiInputOutput (Se esiste)
    content = re.sub(
        r'(struct\s+MidiInputOutput[^\{]*\{)', 
        r'\1' + injection_input, 
        content
    )

    # Fix MidiOutput (Il colpevole dell'ultimo errore)
    content = re.sub(
        r'(struct\s+MidiOutput[^\{]*\{)', 
        r'\1' + injection_output, 
        content
    )
    
    return content

def fix_source_files(content):
    # Sostituzioni standard API VCV 2
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

    # Fix onMessage: Aggiunge la logica di push
    if "onMessage" in content:
        # 1. Firma
        content = content.replace("onMessage(rack::midi::Message message)", "onMessage(const rack::midi::Message& message)")
        
        # 2. Logica Push (Evita doppi inserimenti controllando se c'è già)
        if "messageQueue.push_back" not in content:
            content = re.sub(
                r'(onMessage\(const rack::midi::Message& message\) override\s*\{)', 
                r'\1 messageQueue.push_back(message);', 
                content
            )

    return content

def main():
    print("🤖 AGENTE 23VOLTS: Modalità 'Brute Force'...")
    
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith((".hpp", ".cpp")):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    original = f.read()
                
                content = original
                
                if file.endswith("midi.hpp"):
                    content = fix_header_files(content)
                
                content = fix_source_files(content)

                if content != original:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"🔧 Riparato: {file}")

    print("\n✅ Riparazione completata.")

if __name__ == "__main__":
    main()
