import os

def fix_mapping_hpp():
    path = "src/common/mapping.hpp"
    print(f"🔎 Controllo file: {path}...")
    
    if not os.path.exists(path):
        print(f"❌ Errore: {path} non trovato!")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # --- FIX 1: 'label' deve diventare 'name' ---
    # Errore log: 'struct rack::engine::ParamQuantity' has no member named 'label'
    if "paramQuantity->label" in content:
        print("   -> Trovato 'paramQuantity->label', correggo in 'name'...")
        content = content.replace("paramQuantity->label", "paramQuantity->name")
    
    # --- FIX 2: MappingProcessor non ha getParamQuantity() ---
    # Errore log: 'struct MappingProcessor' has no member named 'getParamQuantity'
    # Qui il codice errato è: this->getParamQuantity()->setScaledValue(value);
    # Deve tornare ad essere: paramQuantity->setScaledValue(value);
    
    bad_line_1 = "this->getParamQuantity()->setScaledValue(value);"
    good_line_1 = "paramQuantity->setScaledValue(value);"
    
    if bad_line_1 in content:
        print("   -> Correggo setScaledValue...")
        content = content.replace(bad_line_1, good_line_1)
        
    # --- FIX 3: Altra chiamata errata in MappingProcessor ---
    # Errore log: mapping->lastTargetValue = getParamQuantity()->getScaledValue();
    
    bad_line_2 = "mapping->lastTargetValue = getParamQuantity()->getScaledValue();"
    good_line_2 = "mapping->lastTargetValue = paramQuantity->getScaledValue();"
    
    if bad_line_2 in content:
        print("   -> Correggo getScaledValue...")
        content = content.replace(bad_line_2, good_line_2)

    # --- FIX 4: Pulizia residui generici in quel file ---
    # Se ci sono altri "getParamQuantity()->" che dovrebbero essere "paramQuantity->"
    # Lo facciamo solo se preceduti da "if (!" come visto nei log precedenti
    content = content.replace("if (!getParamQuantity()->isBounded())", "if (!paramQuantity->isBounded())")

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ File {path} salvato con le correzioni.")
    else:
        print(f"⚠️ Nessuna modifica necessaria. Il file sembra già corretto o le righe non corrispondono.")

if __name__ == "__main__":
    fix_mapping_hpp()
