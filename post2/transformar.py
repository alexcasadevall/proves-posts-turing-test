import json
import re

def transformar_reddit_a_xat_final(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. Extreure dades del post original (News Card)
        op_data = data[0]['data']['children'][0]['data']
        
        # Netegem també el cos del post original per si té Markdown
        body_original = op_data.get('selftext', '')
        body_original = re.sub(r'(\*\*|__)(.*?)\1', r'<b>\2</b>', body_original)
        body_original = re.sub(r'(\*|_)(.*?)\1', r'<i>\2</i>', body_original)

        post_original = {
            "agency": f"r/{op_data.get('subreddit', 'Reddit')}",
            "title": op_data.get('title', ''),
            "body": body_original,
            "author": op_data.get('author', ''),
            "timestamp": op_data.get('created_utc', 0)
        }

        raw_comments = data[1]['data']['children']
        chat_messages = []
        user_mapping = {}

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
            if 'body' not in c_data: return

            # Gestió de l'autor i pseudònim (Consistent)
            real_author = c_data['author']
            if real_author not in user_mapping:
                if user_counter < len(noms_pool):
                    user_mapping[real_author] = noms_pool[user_counter]
                else:
                    user_mapping[real_author] = f"Participant {user_counter + 1}"
                user_counter += 1
            
            current_name = user_mapping[real_author]
            
            # --- NETEJA DE TEXT I FORMAT (Mantenint paràgrafs) ---
            raw_body = c_data['body']
            
            # 1. ELIMINAR CITES (> text)
            # Usem MULTILINE per detectar el > a l'inici de cada línia i esborrar-la
            clean_text = re.sub(r'^\s*>.*$', '', raw_body, flags=re.MULTILINE)
            
            # 2. MANTENIR ELS SALTS DE LÍNIA (Convertir a <br>)
            # Primer fem un strip per treure espais buits extrems
            clean_text = clean_text.strip()
            # Substituïm els salts de línia per l'etiqueta <br>
            # Usem \n+ per si n'hi ha varis de seguits, que no quedin massa espais buits
            clean_text = clean_text.replace('\n', '<br>')
            
            # 3. FORMAT (Negretes i Cursives)
            clean_text = re.sub(r'(\*\*|__)(.*?)\1', r'<b>\2</b>', clean_text)
            clean_text = re.sub(r'(\*|_)(.*?)\1', r'<i>\2</i>', clean_text)
            
            # 4. NETEJA FINAL D'ESPAIS
            # Substituïm espais múltiples (però no els <br>) per un de sol
            clean_text = re.sub(r'[ \t]+', ' ', clean_text)
            
            if not clean_text: clean_text = "..."
            
            textos_per_id[c_data['id']] = clean_text

            parent_text = ""
            if parent_id and parent_id in textos_per_id:
                parent_text = textos_per_id[parent_id]

            message = {
                "id": c_data['id'],
                "sender": current_name,
                "real_author": real_author, # Guardem l'original per si el necessites
                "text": clean_text,
                "timestamp": c_data['created_utc'],
                "reply_to": parent_author,
                "reply_text": parent_text[:85] + "..." if len(parent_text) > 85 else parent_text,
                "likes": abs(hash(c_data['id'])) % 7 
            }
            chat_messages.append(message)

            replies = c_data.get('replies')
            if replies and isinstance(replies, dict):
                for reply in replies['data']['children']:
                    process_comment(reply, c_data['id'], current_name)

        # Processar tots els comentaris arrel
        for root_comment in raw_comments:
            process_comment(root_comment)

        # Ordenar missatges cronològicament
        chat_messages.sort(key=lambda x: x['timestamp'])
        
        return {
            "post_original": post_original,
            "num_participants": len(user_mapping),
            "messages": chat_messages
        }

    except Exception as e:
        return {"error": str(e)}

# Execució del script
resultat = transformar_reddit_a_xat_final('reddit_thread.json')

if "error" not in resultat:
    with open('conversa_neta.json', 'w', encoding='utf-8') as f:
        json.dump(resultat, f, indent=4, ensure_ascii=False)
    print(f"✅ Fet! S'ha generat 'conversa_neta.json' amb {resultat['num_participants']} participants.")
else:
    print(f"❌ Error: {resultat['error']}")