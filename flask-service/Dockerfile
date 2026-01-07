FROM python:3.11-slim

# 👇 AJOUTE CETTE LIGNE ICI 👇
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copier les dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer le port
EXPOSE 5000

# Lancer l'application
CMD ["python", "app.py"]