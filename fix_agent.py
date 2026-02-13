import os
import re

def fix_manifest():
    path = "plugin.json"
    print(f"🔎 Aggiorno la carta d'identità: {path}...")
    
    if not os.path.exists(path):
        print(f"❌ Errore: {path} non trovato!")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. Cambia la versione del plugin da 1.1.5 a 2.0.0
    # Questo dice a Rack che è una nuova release
    if '"version": "1.1.5"' in content:
        print("   -> Bump version 1.1.5 -> 2.0.0")
        content = content.replace('"version": "1.1.5"', '"version": "2.0.0"')

    # 2. Aggiungi "minRackVersion": "2.0.0"
    # Questo è il passaporto obbligatorio per Rack 2.
    # Lo inseriamo subito dopo la versione per non rompere il JSON.
    if '"minRackVersion"' not in content:
        print("   -> Aggiungo compatibilità Rack 2...")
        content = content.replace('"version": "2.0.0"', '"version": "2.0.0",\n  "minRackVersion": "2.0.0"')

    # 3. Rimuovi vecchia "rackVersion" se esiste (era usata in v1)
    content = re.sub(r'"rackVersion":\s*"[^"]*",?', '', content)

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ plugin.json aggiornato con successo!")
    else:
        print(f"⚠️ Nessuna modifica. Controlla se plugin.json è già aggiornato.")

if __name__ == "__main__":
    fix_manifest()
