import os
import re

def fix_header_files(content):
    # 1. Aggiunge <deque> se manca
    if "struct MidiInput" in content and "#include <deque>" not in content:
        content = "#include <deque>\n" + content

    # Definizioni da iniettare
    queue_decl = " std::deque<rack::midi::Message> messageQueue; "
    shift_func = " bool shift(rack::midi::Message *msg) { if (messageQueue.empty()) return false; *msg = messageQueue.front(); messageQueue.pop_front(); return true; } "

    # 2. INIEZIONE SICURA (Controlla se c'è già)
    if "bool shift" not in content:
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

    if "struct MidiOutput" in content and "messageQueue;" not in content:
        content = re.sub(
            r'(struct\s+MidiOutput\s*:\s*(?:rack::)?midi::Output\s*\{)', 
            r'\1' + queue_decl, 
            content
        )
    
    return content

def cleanup_recursive_mess(content):
    """Rimuove le ripetizioni tipo rack::ui::rack::ui::"""
    # Continua a pulire finché non trova più duplicati
    has_changed = True
    while has_changed:
        original = content
        content = content.replace("rack::engine::Port::rack::engine::Port::", "rack::engine::Port::")
        content = content.replace("rack::ui::rack::ui::", "rack::ui::")
        content = content.replace("rack::app::rack::app::", "rack::app::")
        content = content.replace("rack::rack::", "rack::") # Caso generico
        has_changed = (content != original)
    return content

def fix_source_files(content):
    # 1. PULIZIA PREVENTIVA
    content = cleanup_recursive_mess(content)

    # 2. SOSTITUZIONI INTELLIGENTI
    # (?<!::) significa "Sostituisci SOLO se davanti NON c'è '::'"
    # Questo impedisce di rompere codice già corretto.
    replacements = [
        (r'(?<!::)\bINPUT\b', 'rack::engine::Port::INPUT'),
        (r'(?<!::)\bOUTPUT\b', 'rack::engine::Port::OUTPUT'),
        (r'(?<!::)\bMenuLabel\b', 'rack::ui::MenuLabel'),
        (r'(?<!::)\bLabel\b', 'rack::app::Label'),
        # Per paramQuantity è più sicuro usare stringhe semplici
        (r'paramQuantity->', 'getParamQuantity()->'),
        (r'getParamQuantity\(\)->getParamQuantity\(\)->', 'getParamQuantity()->'), # Fix per doppi inserimenti
        (r'delete cells;', 'delete[] cells;'),
        (r'std::auto_ptr', 'std::unique_ptr'),
    ]
    
    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    # 3. FIX onMessage (Safe)
    if "onMessage" in content:
        content = content.replace("onMessage(rack::midi::Message message)", "onMessage(const rack::midi::Message& message)")
        # Inietta solo se non c'è già il push
        if "messageQueue.push_back" not in content:
            content = re.sub(
                r'(onMessage\(const rack::midi::Message& message\) override\s*\{)', 
                r'\1 messageQueue.push_back(message);', 
                content
            )

    return content

def main():
    print("🤖 AGENTE 23VOLTS: Pulizia Recursion & Fix...")
    
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith((".hpp", ".cpp")):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        original = f.read()
                    
                    content = original
                    
                    if file.endswith(".hpp"):
                        content = fix_header_files(content)
                    
                    content = fix_source_files(content)

                    if content != original:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"🧹 Pulito e Riparato: {file}")
                except Exception as e:
                    print(f"Errore {file}: {e}")

    print("\n✅ Codice sanificato. Esegui git push.")

if __name__ == "__main__":
    main()
