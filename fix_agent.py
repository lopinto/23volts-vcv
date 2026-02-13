import os
import re

def clean_midi_header(content):
    """Rimuove TUTTE le iniezioni precedenti per ripartire da zero"""
    print("   -> Spurgo duplicati in midi.hpp...")
    
    # 1. Rimuove le righe che contengono la nostra coda
    # Usiamo una regex che cattura la nostra definizione specifica
    content = re.sub(r'\s*std::deque<rack::midi::Message> messageQueue;\s*', '', content)
    
    # 2. Rimuove le righe che contengono la funzione shift manuale
    content = re.sub(r'\s*bool shift\(rack::midi::Message \*msg\).*?\}\s*', '', content, flags=re.DOTALL)
    
    # 3. Rimuove eventuali include doppi di deque
    content = content.replace("#include <deque>\n", "") 
    
    return content

def patch_midi_header(content):
    """Applica la patch pulita UNA VOLTA SOLA"""
    
    # 1. Rimette l'include (una volta sola, in cima)
    content = "#include <deque>\n" + content

    # Definizioni da iniettare
    queue_decl = " std::deque<rack::midi::Message> messageQueue; "
    shift_func = " bool shift(rack::midi::Message *msg) { if (messageQueue.empty()) return false; *msg = messageQueue.front(); messageQueue.pop_front(); return true; } "

    # 2. INIEZIONE (Ora siamo sicuri che il file è pulito)
    
    # Fix MidiInput
    content = re.sub(
        r'(struct\s+MidiInput\s*:\s*(?:rack::)?midi::Input\s*\{)', 
        r'\1' + queue_decl + shift_func, 
        content
    )

    # Fix MidiInputOutput
    content = re.sub(
        r'(struct\s+MidiInputOutput\s*:\s*(?:rack::)?midi::Input\s*\{)', 
        r'\1' + queue_decl + shift_func, 
        content
    )

    # Fix MidiOutput
    content = re.sub(
        r'(struct\s+MidiOutput\s*:\s*(?:rack::)?midi::Output\s*\{)', 
        r'\1' + queue_decl, 
        content
    )
    
    return content

def fix_source_files(content):
    # Sostituzioni standard (con controllo "lookbehind" per non farlo due volte)
    replacements = [
        (r'(?<!::)\bINPUT\b', 'rack::engine::Port::INPUT'),
        (r'(?<!::)\bOUTPUT\b', 'rack::engine::Port::OUTPUT'),
        (r'(?<!::)\bMenuLabel\b', 'rack::ui::MenuLabel'),
        (r'(?<!::)\bLabel\b', 'rack::app::Label'),
        (r'paramQuantity->', 'getParamQuantity()->'),
        (r'getParamQuantity\(\)->getParamQuantity\(\)->', 'getParamQuantity()->'), # Fix doppi
        (r'delete cells;', 'delete[] cells;'),
        (r'std::auto_ptr', 'std::unique_ptr'),
    ]
    
    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    # Fix onMessage
    if "onMessage" in content:
        content = content.replace("onMessage(rack::midi::Message message)", "onMessage(const rack::midi::Message& message)")
        
        # Pulisce eventuali doppi push_back
        content = content.replace("messageQueue.push_back(message); messageQueue.push_back(message);", "messageQueue.push_back(message);")
        
        # Inietta se manca
        if "messageQueue.push_back" not in content:
            content = re.sub(
                r'(onMessage\(const rack::midi::Message& message\) override\s*\{)', 
                r'\1 messageQueue.push_back(message);', 
                content
            )

    return content

def main():
    print("🤖 AGENTE 23VOLTS: Modalità 'Idraulico' (Pulisci e Ripara)...")
    
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith((".hpp", ".cpp")):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        original = f.read()
                    
                    content = original
                    
                    # LOGICA SPECIFICA PER MIDI.HPP
                    if file.endswith("midi.hpp"):
                        # Fase 1: Rimuovi tutto il vecchio (Clean)
                        content = clean_midi_header(content)
                        # Fase 2: Metti il nuovo (Patch)
                        content = patch_midi_header(content)
                    
                    # LOGICA GENERALE
                    content = fix_source_files(content)

                    if content != original:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"🧹 Pulito e Riparato: {file}")
                except Exception as e:
                    print(f"Errore {file}: {e}")

    print("\n✅ Duplicati rimossi. Ora puoi fare il push.")

if __name__ == "__main__":
    main()
