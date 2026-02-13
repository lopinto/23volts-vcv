import os
import re

def fix_mapping_logic(content):
    print("   -> Chirurgia specifica su mapping.hpp...")
    
    # 1. FIX: Rimuove "using TBase::paramQuantity;" 
    # In Rack 2, paramQuantity non è più un membro pubblico, quindi questa riga rompe la compilazione.
    content = content.replace("using TBase::paramQuantity;", "")

    # 2. FIX: Reverte le modifiche errate sulle variabili locali
    # Lo script precedente ha cambiato "paramQuantity->label" in "getParamQuantity()->label"
    # Ma qui paramQuantity è un puntatore locale definito poco sopra. Lo rimettiamo a posto.
    content = content.replace("mapping->paramName = getParamQuantity()->label;", "mapping->paramName = paramQuantity->label;")
    
    # Idem per MappingProcessor: qui paramQuantity sembra essere un membro della classe custom, non di Rack
    content = content.replace("if (!getParamQuantity()->isBounded())", "if (!paramQuantity->isBounded())")
    content = content.replace("float targetParameterValue = getParamQuantity()->getScaledValue();", "float targetParameterValue = paramQuantity->getScaledValue();")

    # 3. FIX: Aggiunge "this->" nei template
    # In MappableParameter<T>, il compilatore non trova getParamQuantity() senza "this->"
    # Sostituiamo le chiamate corrette ma aggiungendo il puntatore this
    content = content.replace("getParamQuantity()->setScaledValue", "this->getParamQuantity()->setScaledValue")
    
    # Attenzione: qui c'è una riga complessa nidificata. La sistemiamo specificamente.
    # Era: getParamQuantity()->setScaledValue(touchedParam->getParamQuantity()->getScaledValue());
    # Deve diventare: this->getParamQuantity()->setScaledValue(touchedParam->getParamQuantity()->getScaledValue());
    # (Notare che touchedParam->getParamQuantity() va bene così com'è)

    return content

def fix_source_files(content, filename):
    # Sostituzioni standard (SOLO SE NON SONO GIÀ STATE FATTE)
    # Usiamo controlli più stretti per evitare doppie sostituzioni
    
    replacements = [
        (r'(?<!::)\bINPUT\b', 'rack::engine::Port::INPUT'),
        (r'(?<!::)\bOUTPUT\b', 'rack::engine::Port::OUTPUT'),
        (r'(?<!::)\bMenuLabel\b', 'rack::ui::MenuLabel'),
        (r'(?<!::)\bLabel\b', 'rack::app::Label'),
        (r'delete cells;', 'delete[] cells;'),
        (r'std::auto_ptr', 'std::unique_ptr'),
    ]
    
    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    # ParamQuantity è delicato. Lo applichiamo solo se NON siamo in mapping.hpp (che gestiamo a parte)
    # o se siamo sicuri che sia un accesso membro.
    if filename != "mapping.hpp":
        content = content.replace("paramQuantity->", "getParamQuantity()->")
        content = content.replace("getParamQuantity()->getParamQuantity()->", "getParamQuantity()->") # Fix doppi

    # Fix onMessage (con controllo anti-duplicati)
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
    print("🤖 AGENTE 23VOLTS: Fixer Chirurgico...")
    
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith((".hpp", ".cpp")):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        original = f.read()
                    
                    content = original
                    
                    # LOGICA SPECIFICA PER MAPPING.HPP
                    if file == "mapping.hpp":
                        content = fix_mapping_logic(content)
                    else:
                        content = fix_source_files(content, file)

                    if content != original:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"🔧 Riparato: {file}")
                except Exception as e:
                    print(f"Errore {file}: {e}")

    print("\n✅ Fix applicati. Esegui git push.")

if __name__ == "__main__":
    main()
