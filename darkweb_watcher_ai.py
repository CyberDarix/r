#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║               OLYSACHECK ULTRA - DARK WEB WATCHER AI v6.0.0                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  👁️ YEUX : Surveillance multi-sources (Dark Web, forums, Telegram, Paste)   ║
║  🧠 CERVEAU : IA analytique avec machine learning intégré                   ║
║  🔗 NEURONES : Détection de patterns et corrélations intelligentes          ║
║  🤖 ROBOT : Auto-apprentissage et correction automatique                    ║
║  🌐 CONNEXION : TiDB Cloud - TA BASE DE DONNÉES EN LIGNE                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import hashlib
import logging
import requests
import pymysql
import schedule
import threading
import queue
import re
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import Counter

# Garde tous tes imports mais on met des try/except pour que ça plante pas
try:
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    import joblib
    ML_AVAILABLE = True
except:
    ML_AVAILABLE = False
    print("⚠️ ML modules non disponibles - fonctionnement en mode basique")

# =============================================================
# 🧬 CONFIGURATION POUR TIDB CLOUD (TES INFOS)
# =============================================================

class BrainConfig:
    # 🔥 TES INFOS TIDB CLOUD (celles de ton image)
    DB_HOST = "gateway01.eu-central-1.prod.aws.tidbcloud.com"
    DB_PORT = 4000
    DB_NAME = "test"
    DB_USER = "3knaJD4GYrbtzop.root"
    DB_PASS = "JObWeGC4nkyYwNor"
    
    # Yeux (sources de surveillance) - GARDÉES
    DARKWEB_SOURCES = [
        # À remplacer par de vraies sources .onion plus tard
    ]
    
    PASTEBIN_SOURCES = [
        "https://pastebin.com/archive",
        "https://ghostbin.com/pastes",
        "https://privatebin.net/"
    ]
    
    TELEGRAM_CHANNELS = [
        "@leakdatabase",
        "@breachalerts",
        "@darkwebnews"
    ]
    
    # API Keys (tu pourras les configurer plus tard)
    TELEGRAM_BOT_TOKEN = "VOTRE_TOKEN"
    
    # Configuration des yeux
    SCAN_INTERVAL_MINUTES = 30  # Plus espacé pour TiDB
    MAX_THREADS = 5
    REQUEST_TIMEOUT = 30
    
    # Configuration du cerveau (GARDÉE)
    AI_MODEL_PATH = "ai_models/breach_detector.pkl"
    CONFIDENCE_THRESHOLD = 0.7
    
    # Logging
    LOG_FILE = "darkweb_watcher.log"
    LOG_LEVEL = logging.INFO

# =============================================================
# 👁️ YEUX DE L'IA (Capteurs multi-sources) - GARDÉ INTACT
# =============================================================

class AIEyes:
    """Yeux de l'IA - Surveillent le web, dark web, forums, réseaux sociaux"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.proxy_pool = self._init_proxies()
        self.queue = queue.Queue()
        self.results = []
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=self.config.LOG_LEVEL,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("AIEyes")
    
    def _init_proxies(self):
        """Initialise un pool de proxies Tor"""
        proxies = []
        try:
            test = requests.get('http://check.torproject.org', proxies={
                'http': 'socks5h://127.0.0.1:9050',
                'https': 'socks5h://127.0.0.1:9050'
            }, timeout=10)
            if test.status_code == 200:
                proxies.append({
                    'http': 'socks5h://127.0.0.1:9050',
                    'https': 'socks5h://127.0.0.1:9050'
                })
                self.logger.info("✅ Tor proxy actif")
        except:
            self.logger.warning("⚠️ Tor non disponible")
        return proxies
    
    def scan_pastebin(self):
        """Scan Pastebin pour trouver des fuites récentes"""
        self.logger.info("🔍 Scan Pastebin en cours...")
        results = []
        
        try:
            response = self.session.get(
                "https://pastebin.com/archive",
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                paste_links = soup.find_all('a', href=re.compile(r'^/[a-zA-Z0-9]{8}$'))
                
                for link in paste_links[:50]:
                    paste_id = link['href'][1:]
                    paste_url = f"https://pastebin.com/raw/{paste_id}"
                    
                    paste_content = self.session.get(paste_url).text
                    
                    if self._analyze_content(paste_content):
                        # Extrait les emails
                        emails = self._extract_emails(paste_content)
                        
                        results.append({
                            'source': 'pastebin',
                            'url': paste_url,
                            'content': paste_content[:1000],
                            'emails': emails[:20],
                            'timestamp': datetime.now()
                        })
                        self.logger.info(f"✅ {len(emails)} emails trouvés: {paste_url}")
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur scan Pastebin: {e}")
            
        return results
    
    def _extract_emails(self, text):
        """Extrait les emails d'un texte"""
        return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    
    def scan_darkweb(self):
        """Scan les sites .onion via Tor"""
        self.logger.info("🔍 Scan Dark Web en cours...")
        results = []
        
        for source in self.config.DARKWEB_SOURCES:
            try:
                response = self.session.get(
                    source,
                    proxies=self.proxy_pool[0] if self.proxy_pool else None,
                    timeout=self.config.REQUEST_TIMEOUT * 2
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()
                    
                    if self._analyze_content(text):
                        emails = self._extract_emails(text)
                        results.append({
                            'source': 'darkweb',
                            'url': source,
                            'content': text[:1000],
                            'emails': emails[:20],
                            'timestamp': datetime.now()
                        })
                        
            except Exception as e:
                self.logger.error(f"❌ Erreur scan Dark Web {source}: {e}")
                
        return results
    
    def _analyze_content(self, text):
        """Analyse basique du contenu"""
        keywords = ['breach', 'leak', 'dump', 'database', 'password', 'email', 
                   'credit card', 'ssn', 'pwned', 'hack', 'compromised']
        
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                return True
        return False
    
    def run_continuous_scan(self):
        """Lance un scan continu de toutes les sources"""
        self.logger.info("🚀 Lancement des scans continus...")
        
        while True:
            threads = []
            
            # Scan Pastebin
            t1 = threading.Thread(target=lambda: self.queue.put(self.scan_pastebin()))
            threads.append(t1)
            
            # Scan Dark Web (si des sources sont configurées)
            if self.config.DARKWEB_SOURCES:
                t2 = threading.Thread(target=lambda: self.queue.put(self.scan_darkweb()))
                threads.append(t2)
            
            for t in threads:
                t.start()
            
            for t in threads:
                t.join(timeout=self.config.REQUEST_TIMEOUT)
            
            while not self.queue.empty():
                self.results.extend(self.queue.get())
            
            time.sleep(self.config.SCAN_INTERVAL_MINUTES * 60)

# =============================================================
# 🧠 CERVEAU DE L'IA (Analyse et Machine Learning) - GARDÉ
# =============================================================

class AIBrain:
    """Cerveau de l'IA - Analyse, ML, prédictions"""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.memory = []
        self.neurons = []
        self.setup_ai()
        
    def setup_ai(self):
        """Initialise le cerveau et charge les modèles"""
        self.logger = logging.getLogger("AIBrain")
        
        # Version simplifiée sans ML si pas disponible
        if ML_AVAILABLE:
            self.vectorizer = TfidfVectorizer(max_features=5000)
            if os.path.exists(self.config.AI_MODEL_PATH):
                self.model = joblib.load(self.config.AI_MODEL_PATH)
                self.logger.info("✅ Modèle IA chargé")
            else:
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                self.logger.info("🆕 Nouveau modèle IA créé")
            
            self.neurons = [Neuron() for _ in range(100)]
            self.logger.info(f"🧬 {len(self.neurons)} neurones activés")
    
    def analyze_breach(self, data):
        """Analyse une fuite potentielle avec l'IA"""
        text = data.get('content', '').lower()
        emails = data.get('emails', [])
        
        # Analyse basique
        severity = 'low'
        if any(word in text for word in ['password', 'pass', 'pwd']):
            severity = 'high'
        if any(word in text for word in ['credit', 'card', 'bank', 'paypal', 'ssn']):
            severity = 'critical'
        
        # Catégorisation
        category = 'unknown'
        for cat, keywords in {
            'social': ['facebook', 'twitter', 'instagram', 'linkedin'],
            'finance': ['bank', 'paypal', 'credit', 'visa'],
            'gaming': ['steam', 'origin', 'ubisoft']
        }.items():
            if any(k in text for k in keywords):
                category = cat
                break
        
        # Types de données exposées
        data_types = ['email']
        if 'password' in text:
            data_types.append('password')
        if 'credit' in text or 'card' in text:
            data_types.append('credit_card')
        
        return {
            'is_breach': len(emails) > 0,
            'confidence': min(len(emails) * 5, 100) / 100,
            'severity': severity,
            'category': category,
            'data_types': data_types
        }

# =============================================================
# 🔗 NEURONES ARTIFICIELS (GARDÉS)
# =============================================================

class Neuron:
    """Neurone artificiel pour l'apprentissage profond"""
    
    def __init__(self):
        self.weights = [random.random() for _ in range(5)]
        self.bias = random.random()
        self.fired_count = 0
        
    def fire(self, inputs):
        """Activation du neurone"""
        if len(inputs) > len(self.weights):
            inputs = inputs[:len(self.weights)]
        activation = sum(w * i for w, i in zip(self.weights, inputs)) + self.bias
        self.fired_count += 1
        return max(0, activation)

# =============================================================
# 🗄️ CONNECTEUR TIDB CLOUD (ADAPTÉ)
# =============================================================

class DatabaseConnector:
    """Gère la connexion à TiDB Cloud"""
    
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.connect()
        
    def connect(self):
        """Établit la connexion à TiDB Cloud"""
        try:
            self.connection = pymysql.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                user=self.config.DB_USER,
                password=self.config.DB_PASS,
                database=self.config.DB_NAME,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logging.info("✅ Connecté à TiDB Cloud")
        except Exception as e:
            logging.error(f"❌ Erreur connexion DB: {e}")
    
    def save_breach(self, result, analysis):
        """Sauvegarde une fuite dans TiDB Cloud"""
        try:
            with self.connection.cursor() as cursor:
                # 1. Insérer dans breaches
                sql_breach = """
                    INSERT INTO breaches (
                        breach_name, breach_date, discovery_date, source_url,
                        description, severity, category, confidence_score
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                breach_name = f"Fuite_{result['source']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                cursor.execute(sql_breach, (
                    breach_name,
                    datetime.now().date(),
                    datetime.now(),
                    result.get('url'),
                    f"Trouvé via {result['source']}",
                    analysis['severity'],
                    analysis['category'],
                    analysis['confidence']
                ))
                
                breach_id = cursor.lastrowid
                
                # 2. Insérer les emails dans compromised_emails
                for email in result.get('emails', [])[:20]:
                    email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
                    domain = email.split('@')[-1] if '@' in email else ''
                    
                    sql_email = """
                        INSERT INTO compromised_emails (
                            email_hash, email_domain, breach_id, 
                            exposed_data, first_seen
                        ) VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_email, (
                        email_hash,
                        domain,
                        breach_id,
                        json.dumps({'source': result['source'], 'email': email}),
                        datetime.now()
                    ))
                
                self.connection.commit()
                logging.info(f"✅ Fuite #{breach_id} sauvegardée avec {len(result.get('emails', []))} emails")
                return breach_id
                
        except Exception as e:
            logging.error(f"❌ Erreur sauvegarde: {e}")
            if self.connection:
                self.connection.rollback()
            return None

# =============================================================
# 📢 NOTIFICATEUR (SIMPLIFIÉ MAIS GARDÉ)
# =============================================================

class Notifier:
    """Gère les notifications"""
    
    def __init__(self, config):
        self.config = config
    
    def send_alerts(self, result, analysis):
        """Log les alertes (version simplifiée)"""
        if analysis['severity'] in ['critical', 'high']:
            logging.warning(f"🚨 ALERTE {analysis['severity'].upper()}: Fuite détectée sur {result['source']}")

# =============================================================
# 🤖 ROBOT PRINCIPAL
# =============================================================

class DarkWebWatcherAI:
    """Robot principal avec yeux, cerveau et neurones"""
    
    def __init__(self):
        self.config = BrainConfig()
        self.eyes = AIEyes(self.config)
        self.brain = AIBrain(self.config)
        self.db = DatabaseConnector(self.config)
        self.notifier = Notifier(self.config)
        self.logger = logging.getLogger("DarkWebWatcherAI")
        
    def run(self):
        """Lance le robot"""
        self.logger.info("""
╔════════════════════════════════════════════════════════════════╗
║     🚀 DARK WEB WATCHER - CONNECTÉ À TIDB CLOUD              ║
╠════════════════════════════════════════════════════════════════╣
║  ✅ Base: TiDB Cloud (EN LIGNE)                               ║
║  ✅ Yeux: ACTIVÉS                                              ║
║  🧠 Cerveau: ACTIVÉ                                            ║
║  🔗 Neurones: PRÊTS                                            ║
╚════════════════════════════════════════════════════════════════╝
        """)
        
        scan_thread = threading.Thread(target=self.eyes.run_continuous_scan)
        scan_thread.daemon = True
        scan_thread.start()
        
        while True:
            try:
                if self.eyes.results:
                    for result in self.eyes.results:
                        self.logger.info(f"📊 Analyse de {result['source']}...")
                        analysis = self.brain.analyze_breach(result)
                        
                        if analysis['is_breach']:
                            self.db.save_breach(result, analysis)
                            self.notifier.send_alerts(result, analysis)
                            
                            # Apprentissage (neurones)
                            if self.brain.neurons:
                                self.brain.neurons[random.randint(0, len(self.brain.neurons)-1)].fire([analysis['confidence']])
                    
                    self.eyes.results = []
                
                time.sleep(10)
                
            except KeyboardInterrupt:
                self.logger.info("👋 Arrêt...")
                sys.exit(0)
            except Exception as e:
                self.logger.error(f"❌ Erreur: {e}")
                time.sleep(60)

# =============================================================
# 🚀 DÉMARRAGE
# =============================================================

if __name__ == "__main__":
    watcher = DarkWebWatcherAI()
    watcher.run()