import os
import re

def fix_mapping_hpp(content):
    print("   -> Chirurgia correttiva su mapping.hpp...")
    
    # 1. FIX API: 'label' è diventato 'name' in ParamQuantity
    content = content.replace("paramQuantity->label", "paramQuantity->name")

    # 2. REVERT: Ripristina la variabile 'paramQuantity' dove è stata cambiata erroneamente in funzione
    # Queste righe sono specifiche di MappingProcessor e l'errore ci dice che vuole la variabile
    
    # Caso: this->getParamQuantity()->setScaledValue(value); -> paramQuantity->setScaledValue(value);
    content = content.replace("this->getParamQuantity()->setScaledValue(value)", "paramQuantity->setScaledValue(value)")
    
    # Caso: mapping->lastTargetValue = getParamQuantity()->getScaledValue(); -> paramQuantity->...
    content = content.replace("mapping->lastTargetValue = getParamQuantity()->getScaledValue()", "mapping->lastTargetValue = paramQuantity->getScaledValue()")

    # Caso: if (!getParamQuantity()->isBounded()) -> paramQuantity->...
    content = content.replace("if (!getParamQuantity()->isBounded())", "if (!paramQuantity->isBounded())")
    
    # Caso generico di revert sicuro (solo se seguito da freccia)
    # Cerchiamo "getParamQuantity()->" che non sia preceduto da "this->" o "touchedParam->" 
    # (perché in MappableParameter invece serve la funzione)
    # Ma per sicurezza usiamo sostituzioni esplicite sopra, o questa regex cauta:
    content = content.replace(" = getParamQuantity()->", " = paramQuantity->")
    
    return content

def main():
    print("🤖 AGENTE 23VOLTS: Fix ParamQuantity & Label...")
    
    path = "src/common/mapping.hpp"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            original = f.read()
        
        content = fix_mapping_hpp(original)

        if content != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"🔧 Riparato: {path}")
        else:
            print(f"⚠️ Nessuna modifica necessaria su {path} (strano, controlla se il file è giusto)")
    else:
        print("❌ File src/common/mapping.hpp non trovato!")

    print("\n✅ Fix applicato. Esegui git push.")

if __name__ == "__main__":
    main()
