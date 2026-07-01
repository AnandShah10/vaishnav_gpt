# views.py — FULLY WORKING ON WSGI (Azure default)

from openai import AzureOpenAI
import json
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render,redirect
import os
import re
import pandas as pd
from .models import Message, LearningProgress, OTP
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
import random

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
    
    "nimbarka": """USER_PROFILE: Nimbarka Sampradaya (Kumara Sampradaya) - Dvaitadvaita philosophy with primary focus on eternal Sri Radha-Krishna as Supreme Absolute.""",

    "gita": """USER_PROFILE: Bhagavad Gita Learning - Focus specifically on the teachings of the Bhagavad Gita, Chapter by Chapter, Sloka by Sloka, providing deep philosophical insights and practical applications.""",
    "bhagavatam": """USER_PROFILE: Srimad Bhagavatam Learning - Focus on the puranic literature of Srimad Bhagavatam, answering questions based on its cantos, chapters, and the pastimes of Lord Krishna and his avatars.""",
    "upanishads": """USER_PROFILE: Upanishads Learning - Provide profound philosophical insights based on the principal Upanishads and Vedanta sutras from a Vaishnava perspective.""",
    "vishnu_puran": """USER_PROFILE: Vishnu Puran Learning - Focus on the stories, cosmology, and philosophy presented in the Vishnu Puran.""",
    "panchang": """USER_PROFILE: Vaishnav Panchang - Act as an expert in Vaishnava calendar (Panchang), Ekadashi dates, tithis, muhurtas, and significant festival dates according to the lunar calendar."""
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
            language = data.get("language", "English")

            session_key = f"vaishnav_chat_{tradition}"
            
            loaded_from_db = False
            
            if request.user.is_authenticated:
                progress_obj, _ = LearningProgress.objects.get_or_create(user=request.user, path=tradition)
                if progress_obj.history:
                    history = progress_obj.history
                    loaded_from_db = True

            if not loaded_from_db:
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
                        {"role": "system", "content": date_prompt},
                        {"role": "system", "content": f"IMPORTANT: You must always respond to the user in {language} language."}
                    ]
                else:
                    history = request.session[session_key]

            history = [m for m in history if not (m.get("role") == "system" and "IMPORTANT: You must always respond" in str(m.get("content", "")))]
            if len(history) >= 2:
                history.insert(2, {"role": "system", "content": f"IMPORTANT: You must always respond to the user in {language} language."})
            else:
                history.append({"role": "system", "content": f"IMPORTANT: You must always respond to the user in {language} language."})

            history.append({"role": "user", "content": user_message})

            def stream_response():
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=history,
                        stream=True
                    )

                    bot_reply = ""
                    for chunk in response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            text = chunk.choices[0].delta.content
                            bot_reply += text
                            yield text

                    # Save to session
                    history.append({"role": "assistant", "content": bot_reply})
                    request.session[session_key] = history
                    request.session.modified = True
                    request.session.save()

                    if hasattr(request, 'user') and request.user.is_authenticated:
                        progress_obj, _ = LearningProgress.objects.get_or_create(user=request.user, path=tradition)
                        progress_obj.history = history
                        progress_obj.save()

                    # Log to DB
                    Message.objects.create(
                        user_message=user_message,
                        bot_reply=bot_reply,
                        timestamp=timezone.now(),
                        tradition=tradition
                    )
                except Exception as e:
                    print("Error:", e)
                    yield "\n\nSorry! I am not able to answer that at the moment."

            response_stream = StreamingHttpResponse(stream_response(), content_type='text/plain')
            user_msg_count = sum(1 for m in history if m.get("role") == "user")
            if user_msg_count == 3:
                response_stream['X-Show-Feedback'] = 'true'
            return response_stream

        except Exception as e:
            print("Error:", e)
            return JsonResponse({"reply": "Sorry! I am not able to answer that at the moment."}, status=500)
    
    # We do not flush the session here anymore because it contains the user's authentication!
    return render(request,"viashnav_bot.html")

@csrf_exempt
def submit_feedback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            phone = data.get("phone")
            email = data.get("email")
            rating = data.get("rating", 0)
            if name and (phone or email):
                from .models import UserFeedback
                UserFeedback.objects.create(name=name, phone=phone, email=email, rating=rating)
                return JsonResponse({"status": "success"})
            return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error"}, status=405)

@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            if not email:
                return JsonResponse({"status": "error", "message": "Email is required."}, status=400)
            
            otp_code = str(random.randint(100000, 999999))
            OTP.objects.filter(email=email).delete()
            OTP.objects.create(email=email, otp_code=otp_code)
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f5; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                    .header {{ background: #0d9488; padding: 24px; text-align: center; color: white; }}
                    .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
                    .content {{ padding: 32px; text-align: center; color: #334155; }}
                    .content p {{ font-size: 16px; line-height: 1.6; margin-bottom: 24px; }}
                    .otp-box {{ background: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 8px; padding: 20px; font-size: 32px; font-weight: 700; color: #0f766e; letter-spacing: 4px; margin-bottom: 24px; }}
                    .footer {{ background: #f8fafc; padding: 16px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Vaishnav GPT</h1>
                    </div>
                    <div class="content">
                        <h2>Your Login Code</h2>
                        <p>Jai Shree Krishna! 🙏<br>Please use the verification code below to sign in to your Vaishnav GPT account. This code will expire in 10 minutes.</p>
                        <div class="otp-box">{otp_code}</div>
                        <p style="font-size: 14px; color: #64748b;">If you didn't request this code, you can safely ignore this email.</p>
                    </div>
                    <div class="footer">
                        &copy; 2026 Vaishnav GPT. All rights reserved.
                    </div>
                </div>
            </body>
            </html>
            """
            
            send_mail(
                subject='Your Vaishnav GPT Login Code',
                message=f'Your OTP code is: {otp_code}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
                html_message=html_content
            )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error"}, status=405)

@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            otp_code = data.get("otp")
            if not email or not otp_code:
                return JsonResponse({"status": "error", "message": "Email and OTP required."}, status=400)
            
            otp_obj = OTP.objects.filter(email=email).last()
            if not otp_obj or otp_obj.otp_code != otp_code or not otp_obj.is_valid():
                return JsonResponse({"status": "error", "message": "Invalid or expired OTP."}, status=400)
            
            user, _ = User.objects.get_or_create(username=email, defaults={'email': email})
            otp_obj.delete()
            
            from django.contrib.auth import login
            login(request, user)
            
            refresh = RefreshToken.for_user(user)
            
            return JsonResponse({
                "status": "success", 
                "token": str(refresh.access_token),
                "refresh": str(refresh),
                "username": user.username
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error"}, status=405)

@csrf_exempt
def get_history(request):
    if request.method == "GET" and request.user.is_authenticated:
        tradition = request.GET.get('tradition', 'universal')
        progress_obj = LearningProgress.objects.filter(user=request.user, path=tradition).first()
        history = progress_obj.history if progress_obj else []
        
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in history if m.get("role") != "system"
        ]
        return JsonResponse({"status": "success", "messages": messages})
    return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)

@csrf_exempt
def logout_user(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=405)
