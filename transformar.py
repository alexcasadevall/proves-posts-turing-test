import json
import re
import os
import glob

def transformar_reddit_a_xat_final(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. POST ORIGINAL (NEWS CARD): Text pur per a .innerText
        op_data = data[0]['data']['children'][0]['data']
        post_original = {
            "agency": f"r/{op_data.get('subreddit', 'Reddit')}",
            "title": op_data.get('title', ''),
            "body": op_data.get('selftext', ''), # Es manté tal qual per a l'HTML simple
            "author": op_data.get('author', ''),
            "timestamp": op_data.get('created_utc', 0)
        }

        # 2. MISSATGES DEL XAT
        raw_comments = data[1]['data']['children']
        all_messages = []
        user_mapping = {}

        # Pool de 60 noms per evitar repeticions
        noms_pool = [
            "Miguel", "Helena", "Alex", "Juan", "Paula", "Clara", "Marc", "Sílvia", "Dani", "Lucía",
            "Sergi", "Carla", "Adrià", "Marta", "Jordi", "Núria", "Pau", "Laia", "Oriol", "Emma",
            "Pol", "Júlia", "Víctor", "Irene", "Albert", "Marina", "Gerard", "Alba", "Oscar", "Sònia",
            "Roger", "Berta", "Xavi", "Anna", "Lluís", "Sara", "Mateu", "Elena", "Ivan", "Noa",
            "Raül", "Queralt", "Eloi", "Aina", "Hugo", "Èric", "Vila", "Nil", "Mar", "Ismael",
            "Biel", "Neus", "Enric", "Clàudia", "Ignasi", "Ivet", "Ramon", "Gisela", "Cesc", "Isona"
        ]
        user_counter = 0
        textos_per_id = {}

        def process_comment(comment_obj, parent_id=None, parent_author=None):
            nonlocal user_counter
            c_data = comment_obj.get('data', {})

            # --- FILTRE DE CONTINGUT ELIMINAT O MODERAT ---
            cos_original = c_data.get('body', '')
            if cos_original in ['[deleted]', '[removed]'] or 'body' not in c_data:
                return 

            autor_original = c_data.get('author', '[deleted]')
            
            # Gestió de pseudònims amb el pool ampliat
            if autor_original not in user_mapping:
                user_mapping[autor_original] = noms_pool[user_counter % len(noms_pool)]
                user_counter += 1
            
            current_name = user_mapping[autor_original]
            
            # --- NETEJA DE TEXT PER AL COS DEL MISSATGE (AMB HTML) ---
            text = cos_original
            text = text.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
            text = re.sub(r'^\s*>.*$', '', text, flags=re.MULTILINE)
            text = re.sub(r'(\*\*|__)(.*?)\1', r'<b>\2</b>', text)
            text = re.sub(r'(\*|_)(.*?)\1', r'<i>\2</i>', text)
            text = text.strip().replace('\n', ' ')
            text = re.sub(r'(<br>\s*){2,}', '<br><br>', text)
            text = re.sub(r'^(<br>)+|(<br>)+$', '', text)

            if not text.strip(): text = "..."
            
            textos_per_id[c_data['id']] = text

            # --- LÒGICA DE REPLY_TEXT (EL TEU CANVI) ---
            reply_display = ""
            if parent_id and parent_id in textos_per_id:
                parent_text_raw = textos_per_id[parent_id]
                # 1. Treure etiquetes HTML (<b>, <i>, <br>) per a la previsualització
                clean_preview = re.sub(r'<[^>]*>', ' ', parent_text_raw).strip()
                # 2. Treure espais duplicats
                clean_preview = re.sub(r'\s+', ' ', clean_preview)
                
                # 3. Només posar punts suspensius si realment tallem (límit 200)
                limit = 200
                if len(clean_preview) > limit:
                    reply_display = clean_preview[:limit] + "..."
                else:
                    reply_display = clean_preview

            message = {
                "id": c_data['id'],
                "sender": current_name,
                "real_author": autor_original,
                "text": text,
                "timestamp": c_data['created_utc'],
                "reply_to": parent_author,
                "reply_text": reply_display,
                "likes": abs(hash(c_data['id'])) % 7 
            }
            all_messages.append(message)

            replies = c_data.get('replies')
            if replies and isinstance(replies, dict):
                for reply in replies['data']['children']:
                    process_comment(reply, c_data['id'], current_name)

        # Processar tot l'arbre de Reddit
        for root_comment in raw_comments:
            process_comment(root_comment)

        # 3. ORDENAR I LIMITAR A 16 MISSATGES
        all_messages.sort(key=lambda x: x['timestamp'])
        final_messages = all_messages[:16]

        # 4. RECALCULAR PARTICIPANTS
        participants_actius = set(m['sender'] for m in final_messages)
        
        return {
            "post_original": post_original,
            "num_participants": len(participants_actius),
            "messages": final_messages
        }

    except Exception as e:
        return {"error": str(e)}

# --- BUCLE DINÀMIC ---
if __name__ == "__main__":
    # Busquem tots els fitxers que compleixin el patró reddit_thread_*.json
    fitxers_reddit = glob.glob("reddit_thread_*.json")
    
    if not fitxers_reddit:
        print("No s'ha trobat cap fitxer 'reddit_thread_*.json' a la carpeta.")
    else:
        # Ordenem els fitxers per nom
        fitxers_reddit.sort()

        for input_file in fitxers_reddit:
            # Extraiem el número per mantenir la coherència en el nom de sortida
            match = re.search(r'reddit_thread_(\d+)\.json', input_file)
            if match:
                output_file = f"conversa_neta_{match.group(1)}.json"
            else:
                output_file = input_file.replace("reddit_thread", "conversa_neta")

            print(f"Processant {input_file}...")
            resultat = transformar_reddit_a_xat_final(input_file)
            
            if "error" not in resultat:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(resultat, f, indent=4, ensure_ascii=False)
                print(f"  ✅ Generat: {output_file}")
            else:
                print(f"  ❌ Error a {input_file}: {resultat['error']}")

        print(f"\n🚀 S'han processat {len(fitxers_reddit)} fitxers (limitats a 16 posts cadascun).")