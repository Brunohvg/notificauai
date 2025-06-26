import os
import sys
import subprocess
import re
from pathlib import Path
from secrets import token_urlsafe

# === CONFIGURAÇÕES INICIAIS === #
PROJETO_DJANGO = "core"
APP_NAME = "accounts"

BASE_DIR = Path(__file__).resolve().parent
APPS_DIR = BASE_DIR / "apps"
APP_PATH = APPS_DIR / APP_NAME
CORE_PATH = BASE_DIR / PROJETO_DJANGO
MANAGE_PATH = BASE_DIR / "manage.py"

# === VERIFICA DEPENDÊNCIAS E INSTALA === #
def instalar_dependencias():
    pacotes = ["django", "python-decouple", "pillow", "psycopg2-binary"]
    #pacotes = ["django", "python-decouple", "pillow"]
    print("🔍 Verificando e instalando dependências...")
    try:
        subprocess.run(["uv", "add"] + pacotes, check=True)
        print("✅ Dependências instaladas com uv.")
    except subprocess.CalledProcessError:
        print("⚠️ uv falhou. Tentando com pip...")
        subprocess.run([sys.executable, "-m", "pip", "install"] + pacotes, check=True)
        print("✅ Dependências instaladas com pip.")
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        exit(1)

# === CRIA ESTRUTURA DE PASTAS (static, templates, media, logs) === #
def criar_pastas_estruturas():
    print("📁 Criando pastas 'static', 'templates', 'media' e 'logs'...")
    (BASE_DIR / "static" / "css").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "static" / "js").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "static" / "img").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "templates").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "media" / "avatars").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)
    print("✅ Pastas criadas.")

# === CRIA O PROJETO DJANGO SE NÃO EXISTIR === #
def criar_projeto_django():
    if not CORE_PATH.exists():
        print(f"⚙️ Criando projeto Django '{PROJETO_DJANGO}'...")
        subprocess.run(["django-admin", "startproject", PROJETO_DJANGO, str(BASE_DIR)], check=True)
        print(f"✅ Projeto '{PROJETO_DJANGO}' criado.")
    else:
        print(f"ℹ️ Projeto '{PROJETO_DJANGO}' já existe.")

# === PREPARA DIRETÓRIO APPS === #
def preparar_diretorio_apps():
    APPS_DIR.mkdir(parents=True, exist_ok=True)
    (APPS_DIR / "__init__.py").touch(exist_ok=True)
    print("✅ Diretório 'apps' preparado.")

# === CRIA O APP ACCOUNTS === #
def criar_app_accounts():
    if not APP_PATH.exists():
        print(f"⚙️ Criando app '{APP_NAME}'...")
        
        # Método 1: Criar app direto no diretório padrão e depois mover
        try:
            temp_app_path = BASE_DIR / APP_NAME
            
            # Primeiro criar o app na raiz
            print("📂 Criando o app temporariamente na raiz...")
            subprocess.run(["uv", "run", str(MANAGE_PATH), "startapp", APP_NAME], check=True)
            
            # Garantir que o diretório de destino exista
            APP_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            # Mover o app para a pasta apps
            if temp_app_path.exists():
                # Se o diretório de destino já existe, remova-o primeiro
                if APP_PATH.exists():
                    import shutil
                    shutil.rmtree(APP_PATH)
                
                # Agora mova o diretório temporário para a pasta apps
                import shutil
                shutil.move(str(temp_app_path), str(APP_PATH))
                print(f"✅ App '{APP_NAME}' criado e movido para a pasta 'apps/'.")
            else:
                print(f"❌ Falha: o diretório temporário '{APP_NAME}' não foi criado.")
                exit(1)
                
        except Exception as e:
            print(f"❌ Erro ao criar app: {e}")
            exit(1)
    else:
        print(f"ℹ️ App '{APP_NAME}' já existe.")

# === ATUALIZA OS ARQUIVOS DO APP === #
def atualizar_arquivos_accounts():
    arquivos = {
        "models.py": '''from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=200, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    notification_email = models.BooleanField(default=True)
    notification_dashboard = models.BooleanField(default=True)

    def __str__(self):
        return f"Perfil de {self.user.email}"
''',
        "managers.py": '''from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser precisa ter is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser precisa ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
''',
        "signals.py": '''from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
''',
        "admin.py": '''from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile

class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'phone', 'company_name')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
''',
        "apps.py": f'''from django.apps import AppConfig

class {APP_NAME.capitalize()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{APP_NAME}'

    def ready(self):
        import apps.{APP_NAME}.signals
'''
    }

    for nome, conteudo in arquivos.items():
        with open(APP_PATH / nome, "w", encoding="utf-8") as f:
            f.write(conteudo)
            
    # Garantir que o arquivo __init__.py exista na pasta migrations
    (APP_PATH / "migrations" / "__init__.py").touch(exist_ok=True)
    
    print("✅ Arquivos do app 'accounts' atualizados.")

# === CRIA O ARQUIVO .env COM VARIÁVEIS IMPORTANTES === #
def criar_arquivo_env():
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        secret_key = token_urlsafe(50)
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f'''SECRET_KEY={secret_key}
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Banco de Dados
DB_ENGINE=django.db.backends.sqlite3
DB_NAME={BASE_DIR / "db.sqlite3"}
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=0

# Configuração de Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu_email@example.com
EMAIL_HOST_PASSWORD=sua_senha

# Logging
LOG_LEVEL=DEBUG
''')
        print("✅ .env criado com SECRET_KEY e variáveis de configuração.")
    else:
        print("ℹ️ Arquivo .env já existe.")

# === AJUSTA O settings.py PARA PADRÃO BR, CONFIGURAÇÕES EXTRA E DATABASE VIA .env === #
def ajustar_settings_py():
    settings_path = CORE_PATH / "settings.py"
    if not settings_path.exists():
        print("❌ settings.py não encontrado.")
        return

    content = settings_path.read_text(encoding="utf-8")
    # Ajuste de imports
    novos_imports = "from decouple import config\nfrom pathlib import Path"
    content = content.replace("from pathlib import Path", novos_imports)
    # Ajustes gerais
    ajustes = {
        "SECRET_KEY = .*": "SECRET_KEY = config('SECRET_KEY')",
        "DEBUG = .*": "DEBUG = config('DEBUG', cast=bool, default=False)",
        "ALLOWED_HOSTS = .*": "ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')",
        "LANGUAGE_CODE = .*": "LANGUAGE_CODE = 'pt-br'",
        "TIME_ZONE = .*": "TIME_ZONE = 'America/Sao_Paulo'",
    }
    for antigo, novo in ajustes.items():
        content = re.sub(antigo, novo, content)
    if "'DIRS': []" in content:
        content = content.replace("'DIRS': []", "'DIRS': [BASE_DIR / 'templates']")
    if "'django.contrib.staticfiles'," in content and "STATICFILES_DIRS" not in content:
        content += "\nSTATICFILES_DIRS = [BASE_DIR / 'static']\n"
    if "'apps.accounts'," not in content:
        content = content.replace(
            "INSTALLED_APPS = [",
            "INSTALLED_APPS = [\n    'apps.accounts',"
        )
    if "MEDIA_URL" not in content:
        content += '''
# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
'''
    if "AUTH_USER_MODEL" not in content:
        content += "\nAUTH_USER_MODEL = 'accounts.User'\n"
    
    # Remover o bloco antigo de DATABASES e adicionar o novo
    content = re.sub(r"DATABASES\s*=\s*\{.*?\n\}", "", content, flags=re.DOTALL)
    content += '''
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', cast=int, default=0),
    }
}
'''

    if "EMAIL_BACKEND" not in content:
        content += '''
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.example.com')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='seu_email@example.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='sua_senha')
'''
    if "LOGGING =" not in content:
        content += '''
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': config('LOG_LEVEL', default='DEBUG'),
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django-debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': config('LOG_LEVEL', default='DEBUG'),
            'propagate': True,
        },
    },
}
'''
    settings_path.write_text(content, encoding="utf-8")
    print("✅ settings.py ajustado com variáveis de banco lidas do .env e demais configurações.")

# === CONFIGURA urls.py PARA SERVIR ARQUIVOS DE MEDIA EM DESENVOLVIMENTO === #
def ajustar_urls_py():
    urls_path = CORE_PATH / "urls.py"
    if not urls_path.exists():
        print("❌ urls.py não encontrado.")
        return

    content = urls_path.read_text(encoding="utf-8")
    if "from django.conf import settings" not in content:
        content = content.replace(
            "from django.urls import path",
            "from django.conf import settings\nfrom django.urls import path\nfrom django.conf.urls.static import static"
        )
    if "urlpatterns +" not in content and "static(settings.MEDIA_URL" not in content:
        content = content.replace(
            "]",
            "]\n\nif settings.DEBUG:\n    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)"
        )
    urls_path.write_text(content, encoding="utf-8")
    print("✅ urls.py ajustado para servir arquivos media em desenvolvimento")

# === CRIA .gitignore PADRÃO === #
def criar_gitignore():
    gitignore_path = BASE_DIR / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text('''\
# Python
__pycache__/
*.py[cod]
*.sqlite3
.env

# Django
static/
media/
db.sqlite3
logs/

# VSCode
.vscode/
''')
        print("✅ .gitignore criado.")

# === RODA MIGRAÇÕES === #
def rodar_migracoes():
    if not MANAGE_PATH.exists():
        print("❌ manage.py não encontrado. Verifique a criação do projeto.")
        exit(1)
    print("⚙️ Rodando makemigrations e migrate...")
    subprocess.run([sys.executable, "manage.py", "makemigrations"], check=True)
    subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
    print("✅ Migrações aplicadas.")

# === CRIA SUPERUSUÁRIO VIA INPUT === #
def criar_superusuario():
    email = input("📧 Email do superusuário: ").strip()
    senha = input("🔐 Senha: ").strip()
    try:
        subprocess.run([sys.executable, "manage.py", "shell", "-c",
                        f"from apps.accounts.models import User; User.objects.create_superuser('{email}', '{senha}')"],
                       check=True)
        print("✅ Superusuário criado.")
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")

# === MAIN === #
def main():
    instalar_dependencias()
    criar_pastas_estruturas()
    criar_projeto_django()
    preparar_diretorio_apps()
    criar_app_accounts()
    atualizar_arquivos_accounts()
    criar_arquivo_env()
    ajustar_settings_py()
    ajustar_urls_py()
    criar_gitignore()
    rodar_migracoes()
    
    if input("Deseja criar o superusuário agora? [s/n]: ").strip().lower() == 's':
        criar_superusuario()

    print("\n🚀 Projeto Django configurado com sucesso!")
    print("👉 Para iniciar, rode: python manage.py runserver")

if __name__ == "__main__":
    main()