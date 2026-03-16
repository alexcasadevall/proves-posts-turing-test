import json
import re

def transformar_reddit_a_xat_final(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. POST ORIGINAL (NEWS CARD)
        op_data = data[0]['data']['children'][0]['data']
        post_original = {
            "agency": f"r/{op_data.get('subreddit', 'Reddit')}",
            "title": op_data.get('title', ''),
            "body": op_data.get('selftext', ''),  
            "author": op_data.get('author', ''),
            "timestamp": op_data.get('created_utc', 0)
        }

        # 2. MISSATGES DEL XAT
        raw_comments = data[1]['data']['children']
        chat_messages = []
        user_mapping = {}

        noms_pool = ["Miguel", "Helena", "Alex", "Juan", "Paula", "Clara", "Marc", "Sílvia", "Dani", "Lucía", "Sergi", "Carla", "Adrià", "Marta", "Jordi"]
        user_counter = 0
        textos_per_id = {}

        def process_comment(comment_obj, parent_id=None, parent_author=None):
            nonlocal user_counter
            c_data = comment_obj.get('data', {})
            if 'body' not in c_data: return

            real_author = c_data['author']
            if real_author not in user_mapping:
                if user_counter < len(noms_pool):
                    user_mapping[real_author] = noms_pool[user_counter]
                else:
                    user_mapping[real_author] = f"Participant {user_counter + 1}"
                user_counter += 1
            
            current_name = user_mapping[real_author]
            
            # --- NETEJA DE TEXT (NOMÉS PER A MISSATGES) ---
            raw_body = c_data['body']
            
            # 1. Decodificar entitats HTML
            text = raw_body.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
            
            # 2. Eliminar línies de cita (Markdown >)
            text = re.sub(r'^\s*>.*$', '', text, flags=re.MULTILINE)
            
            # 3. Format de negretes i cursives
            text = re.sub(r'(\*\*|__)(.*?)\1', r'<b>\2</b>', text)
            text = re.sub(r'(\*|_)(.*?)\1', r'<i>\2</i>', text)
            
            # 4. Convertir salts de línia a <br>
            text = text.strip().replace('\n', '<br>')
            
            # 5. Netejar <br> duplicats
            text = re.sub(r'(<br>\s*){2,}', '<br><br>', text)
            text = re.sub(r'^(<br>)+|(<br>)+$', '', text)

            if not text.strip(): text = "..."
            
            # Guardem el text processat per a les referències de reply
            textos_per_id[c_data['id']] = text

            parent_text = ""
            if parent_id and parent_id in textos_per_id:
                parent_text = textos_per_id[parent_id]

            message = {
                "id": c_data['id'],
                "sender": current_name,
                "real_author": real_author,
                "text": text,
                "timestamp": c_data['created_utc'],
                "reply_to": parent_author,
                # En la previsualització del reply traiem els <br> per a que no es trenqui el disseny
                "reply_text": parent_text.replace('<br>', ' ')[:85] + "...",
                "likes": abs(hash(c_data['id'])) % 7 
            }
            chat_messages.append(message)

            replies = c_data.get('replies')
            if replies and isinstance(replies, dict):
                for reply in replies['data']['children']:
                    process_comment(reply, c_data['id'], current_name)

        for root_comment in raw_comments:
            process_comment(root_comment)

        chat_messages.sort(key=lambda x: x['timestamp'])
        
        return {
            "post_original": post_original,
            "num_participants": len(user_mapping),
            "messages": chat_messages
        }

    except Exception as e:
        return {"error": str(e)}

resultat = transformar_reddit_a_xat_final('reddit_thread.json')

if "error" not in resultat:
    with open('conversa_neta.json', 'w', encoding='utf-8') as f:
        json.dump(resultat, f, indent=4, ensure_ascii=False)
    print(f"✅ Fet! News Card impecable i xat amb format HTML.")
else:
    print(f"❌ Error: {resultat['error']}")