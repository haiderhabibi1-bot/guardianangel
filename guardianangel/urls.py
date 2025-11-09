from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def styled_home(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Guardian Angel</title>
        <style>
            body {
                margin: 0;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                background: radial-gradient(circle at top, #e6f3ff 0%, #c7ddff 40%, #eef4ff 100%);
                color: #404040;
            }
            header {
                background: #dfeeff;
                padding: 14px 32px;
                border-bottom: 2px solid #4a90e2;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                text-align: center;
            }
            h1 {
                color: #333;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            nav {
                text-align: center;
                margin: 16px 0 0;
            }
            nav a {
                text-decoration: none;
                color: #4a4a4a;
                background: #e6f0ff;
                padding: 8px 16px;
                border-radius: 20px;
                margin: 4px;
                display: inline-block;
                transition: 0.2s ease;
                font-weight: 500;
            }
            nav a:hover {
                background: #4a90e2;
                color: white;
                box-shadow: 0 3px 6px rgba(0,0,0,0.15);
            }
            .container {
                max-width: 1080px;
                margin: 40px auto 32px;
                padding: 24px 26px 32px;
                background: rgba(255,255,255,0.98);
                border-radius: 18px;
                box-shadow: 0 14px 40px rgba(0,0,0,0.06);
            }
            h2 {
                color: #555;
                text-shadow: 0 1px 1px #fff, 0 -1px 1px #999;
                margin-top: 0;
            }
            p {
                line-height: 1.6;
                font-size: 1rem;
            }
            footer {
                text-align: center;
                padding: 14px;
                font-size: 0.8rem;
                color: #7a7a7a;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Guardian Angel</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/login/">Login</a>
                <a href="/register/customer/">Sign up (Client)</a>
                <a href="/register/lawyer/">Sign up (Lawyer)</a>
            </nav>
        </header>

        <div class="container">
            <h2>About Us</h2>
            <p>
                At Guardian Angel, we know that sometimes it feels like you have to sign with the devil
                just to make it through. We understand that mental illness can cloud your clarity of mind,
                and that it can feel like you're walking through a storm in a world where phones throw off
                your natural compass. We've been through all the trials, we've seen all the possibilities,
                and we're here so you don't have to go through it all—without risking a human’s mental health
                to do it. We have AI to take care of that. At Guardian Angel, we never lose control, and we
                keep things steady at home. Help us help you. Accept this helping hand—though it may be artificial,
                its impact will be real.
            </p>

            <br><br>
            <h2>À propos de nous</h2>
            <p>
                On le sait chez Guardian Angel que parfois vous sentez qu’il faut signer chez le diable pour
                s’en sortir, on le sait que la maladie mentale vous enlève votre clarté d’esprit et que vous avez
                l’impression de marcher et vous diriger dans une tempête dans un monde où les téléphones
                dérèglent votre boussole naturelle. On est passé par toutes les épreuves, on a vu toutes les
                possibilités et on est là pour que vous n’ayez pas à le faire, sans risquer la santé mentale d’un
                humain pour le faire. On a des AI pour le faire. Chez Guardian Angel, on ne perd jamais les pédales
                et on garde le contrôle à la maison. Aidez-nous à vous aider, acceptez ce coup de main, bien qu’il
                soit artificiel, il sera d’un impact réel.
            </p>
        </div>

        <footer>
            &copy; Guardian Angel. All rights reserved.
        </footer>
    </body>
    </html>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', styled_home, name='home'),
]
