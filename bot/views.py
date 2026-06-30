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

    # Strip dangerous tags first
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)

    # Links: [text](url)
    text = re.sub(
        r'\[([^\]]+)\]\((https?://[^\s)]+|mailto:[^\s)]+)\)',
        r'<a href="\2" target="_blank" rel="noopener noreferrer" class="msg-link">\1</a>',
        text
    )

    # Bold + Italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'___(.+?)___', r'<strong><em>\1</em></strong>', text)

    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

    # Italic (word-boundary aware to avoid false matches)
    text = re.sub(r'(?<!\w)\*([^*\n]+?)\*(?!\w)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!\w)_([^_\n]+?)_(?!\w)', r'<em>\1</em>', text)

    # Process line-by-line for headings, lists, etc.
    lines = text.split('\n')
    html_lines = []
    in_ul = False
    in_ol = False

    for line in lines:
        stripped = line.strip()

        # Headings
        if stripped.startswith('#### '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f'<h4>{stripped[5:]}</h4>')
            continue
        if stripped.startswith('### '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f'<h3>{stripped[4:]}</h3>')
            continue
        if stripped.startswith('## '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f'<h2>{stripped[3:]}</h2>')
            continue
        if stripped.startswith('# '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f'<h2>{stripped[2:]}</h2>')
            continue

        # Unordered list items (- or *)
        ul_match = re.match(r'^[-*]\s+(.+)$', stripped)
        if ul_match:
            if in_ol: html_lines.append('</ol>'); in_ol = False
            if not in_ul: html_lines.append('<ul>'); in_ul = True
            html_lines.append(f'<li>{ul_match.group(1)}</li>')
            continue

        # Ordered list items (1. 2. etc.)
        ol_match = re.match(r'^\d+\.\s+(.+)$', stripped)
        if ol_match:
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if not in_ol: html_lines.append('<ol>'); in_ol = True
            html_lines.append(f'<li>{ol_match.group(1)}</li>')
            continue

        # Close any open lists on non-list lines
        if in_ul: html_lines.append('</ul>'); in_ul = False
        if in_ol: html_lines.append('</ol>'); in_ol = False

        # Empty line = paragraph break
        if not stripped:
            html_lines.append('<br>')
            continue

        # Regular text as paragraph
        html_lines.append(f'<p>{stripped}</p>')

    # Close any still-open lists
    if in_ul: html_lines.append('</ul>')
    if in_ol: html_lines.append('</ol>')

    return '\n'.join(html_lines)

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
                model="gpt-4o-mini",
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
