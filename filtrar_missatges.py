import json
import os
import glob

def filtrar_conversa_recursiva(input_file, output_file, ids_inicials):
    try:
        if not os.path.exists(input_file): return

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        missatges = data.get('messages', [])
        ids_a_eliminar = set(ids_inicials)
        
        trobat_nou = True
        while trobat_nou:
            trobat_nou = False
            for m in missatges:
                if m['parent_id'] in ids_a_eliminar and m['id'] not in ids_a_eliminar:
                    ids_a_eliminar.add(m['id'])
                    trobat_nou = True

        sobreviscuts = [m for m in missatges if m['id'] not in ids_a_eliminar]
        
        data['messages'] = sobreviscuts
        data['num_participants'] = len(set(m['sender'] for m in sobreviscuts))

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ {input_file}: Eliminats {len(ids_a_eliminar)} missatges (branca completa).")

    except Exception as e:
        print(f"❌ Error a {input_file}: {e}")

# --- CONFIGURACIÓ ---
ids_a_eliminar = ["POSA_ID_MSSG_ELIMINAR"] 

if __name__ == "__main__":
    fitxers = glob.glob("conversa_neta_*.json")
    for f in fitxers:
        filtrar_conversa_recursiva(f, f, ids_a_eliminar) 