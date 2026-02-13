import os
import re

def fix_midi_header(content):
    print("   -> Analisi midi.hpp (Modalità Blind Inject)...")
    
    # 1. Assicura che ci sia <deque>
    if "#include <deque>" not in content:
        content = "#include <deque>\n" + content

    # Definizioni da iniettare
    queue_decl = " std::deque<rack::midi::Message> messageQueue; "
    shift_func = " bool shift(rack::midi::Message *msg) { if (messageQueue.empty()) return false; *msg = messageQueue.front(); messageQueue.pop_front(); return true; } "

    # 2. INIEZIONE "BRUTE FORCE" (Regex permissive)
    # Cerca "struct MidiInput" seguito da QUALSIASI COSA fino alla prima graffa "{"
    
    # Fix MidiInput (Se non c'è già la coda)
    if "std::deque" not in content or "struct MidiInput" in content: 
         # Nota: controlliamo specificamente dentro i blocchi dopo
         pass

    # Strategia: Sostituzione diretta basata sul nome della struct
    
    # Fix MidiInput
    content = re.sub(
        r'(struct\s+MidiInput\b[^\{]*\{)', 
        r'\1' + queue_decl + shift_func, 
        content
    )

    # Fix MidiInputOutput
    content = re.sub(
        r'(struct\s+MidiInputOutput\b[^\{]*\{)', 
        r'\1' + queue_decl + shift_func, 
        content
    )

    # Fix MidiOutput
    content = re.sub(
        r'(struct\s+MidiOutput\b[^\{]*\{)', 
        r'\1' + queue_decl, 
        content
    )
    
    # Pulizia finale (se per caso l'abbiamo inserito due volte per via del loop precedente)
    # Rimuove duplicati adiacenti
    content = content.replace(queue_decl + queue_decl, queue_decl)
    content = content.replace(shift_func + shift_func, shift_func)
    
    return content

def fix_source_files(content):
    # Solite sostituzioni API
    replacements = [
        (r'(?<!::)\bINPUT\b', 'rack::engine::Port::INPUT'),
        (r'(?<!::)\bOUTPUT\b', 'rack::engine::Port::OUTPUT'),
        (r'(?<!::)\bMenuLabel\b', 'rack::ui::MenuLabel'),
        (r'(?<!::)\bLabel\b', 'rack::app::Label'),
        (r'paramQuantity->', 'getParamQuantity()->'),
        (r'delete cells;', 'delete[] cells;'),
        (r'std::auto_ptr', 'std::unique_ptr'),
    ]
    
    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    # Fix onMessage
    if "onMessage" in content:
        content = content.replace("onMessage(rack::midi::Message message)", "onMessage(const rack::midi::Message& message)")
        if "messageQueue.push_back" not in content:
            content = re.sub(
                r'(onMessage\(const rack::midi::Message& message\) override\s*\{)', 
                r'\1 messageQueue.push_back(message);', 
                content
            )

    return content

def main():
    print("🤖 AGENTE 23VOLTS: Injector...")
    
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith((".hpp", ".cpp")):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        original = f.read()
                    
                    content = original
                    
                    if file.endswith("midi.hpp"):
                        content = fix_midi_header(content)
                    
                    content = fix_source_files(content)

                    if content != original:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"🔧 Iniettato: {file}")
                except Exception as e:
                    print(f"Errore {file}: {e}")

    print("\n✅ Fatto. Esegui git push.")

if __name__ == "__main__":
    main()
