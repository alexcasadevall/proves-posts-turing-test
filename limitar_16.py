import json
import glob
import re
import os

def limitar_a_16_respostes():
    # 1. Busquem tots els fitxers conversa_neta_x.json
    fitxers = glob.glob("conversa_neta_*.json")
    
    if not fitxers:
        print("No s'han trobat fitxers que comencin per 'conversa_neta_'.")
        return

    for ruta_fitxer in fitxers:
        # Extraurem el número per mantenir la coherència
        match = re.search(r'conversa_neta_(\d+)\.json', ruta_fitxer)
        if not match:
            continue
        
        num = match.group(1)
        nom_sortida = f"conversa_neta_limit16_{num}.json"
        
        try:
            with open(ruta_fitxer, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            missatges = data.get('messages', [])
            total_actual = len(missatges)

            # 2. Si té més de 16, retallem
            if total_actual > 16:
                print(f"File {ruta_fitxer}: Retallant de {total_actual} a 16 missatges.")
                nous_missatges = missatges[:16]
            else:
                print(f"File {ruta_fitxer}: Té {total_actual} missatges (es queda igual).")
                nous_missatges = missatges

            # 3. Actualitzem la llista i el comptador de participants
            data['messages'] = nous_missatges
            participants_reals = set(m['sender'] for m in nous_missatges)
            data['num_participants'] = len(participants_reals)

            # 4. Guardem el nou fitxer
            with open(nom_sortida, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"   ✅ Guardat com a: {nom_sortida}")

        except Exception as e:
            print(f"   ❌ Error processant {ruta_fitxer}: {e}")

if __name__ == "__main__":
    limitar_a_16_respostes()