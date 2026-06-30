# views.py — FULLY WORKING ON WSGI (Azure default)

from openai import AzureOpenAI
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render
import os
import re
import pandas as pd
from .models import  Message
from django.utils import timezone

client = AzureOpenAI(api_key=settings.OPENAI_API_KEY,azure_endpoint=settings.ENDPOINT_URL,api_version="2024-05-01-preview")

def load_kb_file(relative_path):
    """
    Load a KB file from the static folder and return its text.
    """
    full_path = os.path.join(settings.BASE_DIR, "static", relative_path)

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PROMPT = load_kb_file("KB.txt")

def markdown_to_html(text: str) -> str:
    if not text:
        return ""
    
    # Links: [text](url)
    # Allows http, https, and mailto links
    link_text = re.sub(
        r'\[([^\]]+)\]\((https?:\/\/[^\s)]+|mailto:[^\s)]+)\)',
        r'<a href="\2" target="_blank" rel="noopener noreferrer" style="color:blue;cursor:pointer;">\1</a>',
        text
    )
    if link_text:
        return link_text
    
    # Bold + Italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'___(.+?)___', r'<b><i>\1</i></b>', text)
    
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    
    # Replace newlines with <br>
    text = text.replace("\n", "<br>")
    
    # Strip dangerous tags
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text

TRADITION_PROFILES = {
    "universal": "USER_PROFILE: Universal Vaishnava - General Bhakti covering all four Sampradayas with emphasis on core principles.",
    
    "krishna": """USER_PROFILE: Krishna Bhakti (Gaudiya / Brahma Sampradaya) - Deep expertise in Radha-Krishna, Chaitanya Mahaprabhu, Srimad Bhagavatam, Chaitanya Charitamrita, and Achintya Bheda Abheda philosophy.""",
    
    "ram": """USER_PROFILE: Rama Bhakti (Sri / Ramanandi Sampradaya) - Expertise in Lord Rama, Sita-Rama, Hanuman, Vishishtadvaita philosophy, and Ramananda tradition.""",
    
    "vallabha": """USER_PROFILE: Pushtimarg (Rudra Sampradaya - Vallabhacharya) - Pure Monism (Shuddhadvaita), Pushti Marg, Shrinathji Sewa, and Ashta-Chhap poets.""",
    
    "nimbarka": """USER_PROFILE: Nimbarka Sampradaya (Kumara Sampradaya) - Dvaitadvaita philosophy with primary focus on eternal Sri Radha-Krishna as Supreme Absolute."""
}

def get_system_prompt_with_tradition(tradition):
    profile = TRADITION_PROFILES.get(tradition, TRADITION_PROFILES["universal"])
    return f"{SYSTEM_PROMPT}\n\n{profile}"

@csrf_exempt
def vaishnav_bot(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()
            tradition = data.get("tradition", "universal")   # From frontend selection

            session_key = f"vaishnav_chat_{tradition}"

            if session_key not in request.session:
                now = timezone.now()
                date_str = now.strftime("%A, %B %d, %Y")
                time_str = now.strftime("%H:%M UTC")
                date_prompt = (
                    f"Current date and time: {date_str} at {time_str}. "
                    "Use this only for well-known calendar associations."
                )

                full_system_prompt = get_system_prompt_with_tradition(tradition)

                history = [
                    {"role": "system", "content": full_system_prompt},
                    {"role": "system", "content": date_prompt}
                ]
            else:
                history = request.session[session_key]

            history.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model="gpt-5.3-chat",
                messages=history,
            )

            bot_reply = response.choices[0].message.content.strip()
            bot_reply = markdown_to_html(bot_reply)
            history.append({"role": "assistant", "content": bot_reply})
            # Save to session
            request.session[session_key] = history
            request.session.modified = True

            # Optional: Log to DB
            Message.objects.create(
                user_message=user_message,
                bot_reply=bot_reply,
                timestamp=timezone.now(),
                tradition=tradition
            )

            return JsonResponse({
                "reply": bot_reply,
                "tradition": tradition
            })

        except Exception as e:
            print("Error:", e)
            return JsonResponse({"reply": "Sorry! I am not able to answer that at the moment."})
    request.session.flush()
    return render(request,"viashnav_bot.html")
