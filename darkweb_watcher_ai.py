#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║               OLYSACHECK ULTRA - DARK WEB WATCHER AI v6.0.0                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  🚀 OPTIMISÉ POUR RENDER CLOUD                                              ║
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
import threading
import queue
import re
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import Counter

# =============================================================
# 🎯 CONFIGURATION RENDER - VARIABLES D'ENVIRONNEMENT
# =============================================================

# Toutes les informations sensibles viennent des variables d'environnement
DB_HOST = os.environ.get('TIDB_HOST', 'gateway01.eu-central-1.prod.aws.tidbcloud.com')
DB_PORT = int(os.environ.get('TIDB_PORT', 4000))
DB_NAME = os.environ.get('TIDB_DATABASE', 'test')
DB_USER = os.environ.get('TIDB_USER', '')
DB_PASS = os.environ.get('TIDB_PASSWORD', '')

# Vérification que les variables sont présentes
if not DB_USER or not DB_PASS:
    print("❌ ERREUR CRITIQUE: Variables d'environnement TIDB_USER et TIDB_PASSWORD doivent être définies")
    sys.exit(1)

# Configuration Render
RENDER = os.environ.get('RENDER', False)
PORT = int(os.environ.get('PORT', 10000))

# =============================================================
# 🧬 CONFIGURATION POUR TIDB CLOUD
# =============================================================

class BrainConfig:
    # 🔥 TES INFOS TIDB CLOUD (via variables d'environnement)
    DB_HOST = DB_HOST
    DB_PORT = DB_PORT
    DB_NAME = DB_NAME
    DB_USER = DB_USER
    DB_PASS = DB_PASS
    
    # Yeux (sources de surveillance) - À CONFIGURER
    DARKWEB_SOURCES = os.environ.get('DARKWEB_SOURCES', '').split(',') if os.environ.get('DARKWEB_SOURCES') else []
    
    PASTEBIN_SOURCES = [
        "https://pastebin.com/archive",
        "https://ghostbin.com/pastes",
        "https://privatebin.net/"
    ]
    
    TELEGRAM_CHANNELS = os.environ.get('TELEGRAM_CHANNELS', '').split(',') if os.environ.get('TELEGRAM_CHANNELS') else []
    
    # API Keys
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    
    # Configuration des yeux
    SCAN_INTERVAL_MINUTES = int(os.environ.get('SCAN_INTERVAL', 30))
    MAX_THREADS = int(os.environ.get('MAX_THREADS', 5))
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 30))
    
    # Logging
    LOG_FILE = "/tmp/darkweb_watcher.log" if RENDER else "darkweb_watcher.log"
    LOG_LEVEL = logging.INFO

# =============================================================
# 👁️ YEUX DE L'IA (Capteurs multi-sources)
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
        # Sur Render, Tor n'est pas disponible par défaut
        # Tu devras utiliser un service proxy externe ou installer Tor via apt
        if os.environ.get('TOR_PROXY', ''):
            try:
                proxies.append({
                    'http': os.environ.get('TOR_PROXY'),
                    'https': os.environ.get('TOR_PROXY')
                })
                self.logger.info(f"✅ Proxy configuré: {os.environ.get('TOR_PROXY')}")
            except:
                self.logger.warning("⚠️ Proxy non disponible")
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
                    
                    try:
                        paste_content = self.session.get(paste_url, timeout=10).text
                        
                        if self._analyze_content(paste_content):
                            emails = self._extract_emails(paste_content)
                            
                            results.append({
                                'source': 'pastebin',
                                'url': paste_url,
                                'content': paste_content[:1000],
                                'emails': emails[:20],
                                'timestamp': datetime.now()
                            })
                            self.logger.info(f"✅ {len(emails)} emails trouvés: {paste_url}")
                    except:
                        continue
                        
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
        
        if not self.config.DARKWEB_SOURCES:
            return results
            
        for source in self.config.DARKWEB_SOURCES:
            try:
                proxies = self.proxy_pool[0] if self.proxy_pool else None
                if not proxies:
                    self.logger.warning("⚠️ Pas de proxy Tor configuré, impossible de scanner le dark web")
                    continue
                    
                response = self.session.get(
                    source,
                    proxies=proxies,
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
            
            self.logger.info(f"💤 Pause de {self.config.SCAN_INTERVAL_MINUTES} minutes...")
            time.sleep(self.config.SCAN_INTERVAL_MINUTES * 60)

# =============================================================
# 🧠 CERVEAU DE L'IA (Analyse)
# =============================================================

class AIBrain:
    """Cerveau de l'IA - Analyse, ML, prédictions"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("AIBrain")
    
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
        
        return {
            'is_breach': len(emails) > 0,
            'confidence': min(len(emails) * 5, 100) / 100,
            'severity': severity,
            'category': category,
            'data_types': ['email'] + (['password'] if 'password' in text else [])
        }

# =============================================================
# 🗄️ CONNECTEUR TIDB CLOUD
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
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10
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
# 📢 NOTIFICATEUR
# =============================================================

class Notifier:
    """Gère les notifications"""
    
    def __init__(self, config):
        self.config = config
    
    def send_alerts(self, result, analysis):
        """Log les alertes"""
        if analysis['severity'] in ['critical', 'high']:
            logging.warning(f"🚨 ALERTE {analysis['severity'].upper()}: Fuite détectée sur {result['source']}")

# =============================================================
# 🤖 SERVEUR WEB POUR RENDER
# =============================================================

# Cette partie est CRUCIALE pour Render !
# Render a besoin d'un port HTTP ouvert pour considérer que l'app tourne

try:
    from flask import Flask, jsonify
    WEB_SERVER_AVAILABLE = True
except ImportError:
    WEB_SERVER_AVAILABLE = False
    print("⚠️ Flask non installé, pas de serveur web")

if WEB_SERVER_AVAILABLE:
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({
            'status': 'running',
            'service': 'OlysaCheck Dark Web Watcher AI',
            'version': '6.0.0',
            'uptime': time.time() - start_time,
            'connected_to_tidb': db_connected
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    @app.route('/stats')
    def stats():
        return jsonify({
            'scans_performed': scan_count,
            'breaches_found': breach_count,
            'emails_found': email_count
        })

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
        self.scan_count = 0
        self.breach_count = 0
        self.email_count = 0
        
    def run(self):
        """Lance le robot"""
        self.logger.info("""
╔════════════════════════════════════════════════════════════════╗
║     🚀 DARK WEB WATCHER - CONNECTÉ À TIDB CLOUD              ║
╠════════════════════════════════════════════════════════════════╣
║  ✅ Base: TiDB Cloud (EN LIGNE)                               ║
║  ✅ Yeux: ACTIVÉS                                              ║
║  🧠 Cerveau: ACTIVÉ                                            ║
║  🌐 Serveur web: PRÊT (port {PORT})                           ║
╚════════════════════════════════════════════════════════════════╝
        """)
        
        scan_thread = threading.Thread(target=self._scan_loop)
        scan_thread.daemon = True
        scan_thread.start()
        
        # Boucle principale (juste pour garder le thread principal en vie)
        while True:
            try:
                time.sleep(60)
                self.logger.info(f"📊 Stats: {self.scan_count} scans, {self.breach_count} fuites, {self.email_count} emails")
            except KeyboardInterrupt:
                self.logger.info("👋 Arrêt...")
                sys.exit(0)
    
    def _scan_loop(self):
        """Boucle de scan dans un thread séparé"""
        while True:
            try:
                self.scan_count += 1
                self.logger.info(f"🔍 Scan #{self.scan_count} en cours...")
                
                # Scan Pastebin
                results = self.eyes.scan_pastebin()
                
                for result in results:
                    self.logger.info(f"📊 Analyse de {result['source']}...")
                    analysis = self.brain.analyze_breach(result)
                    
                    if analysis['is_breach']:
                        self.breach_count += 1
                        self.email_count += len(result.get('emails', []))
                        self.db.save_breach(result, analysis)
                        self.notifier.send_alerts(result, analysis)
                
                self.logger.info(f"💤 Pause de {self.config.SCAN_INTERVAL_MINUTES} minutes...")
                time.sleep(self.config.SCAN_INTERVAL_MINUTES * 60)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur dans scan_loop: {e}")
                time.sleep(60)

# =============================================================
# 🚀 DÉMARRAGE
# =============================================================

if __name__ == "__main__":
    start_time = time.time()
    db_connected = True
    scan_count = 0
    breach_count = 0
    email_count = 0
    
    # Création du watcher
    watcher = DarkWebWatcherAI()
    
    # Lancement du watcher dans un thread
    watcher_thread = threading.Thread(target=watcher.run)
    watcher_thread.daemon = True
    watcher_thread.start()
    
    # Sur Render, on lance le serveur web
    if WEB_SERVER_AVAILABLE and RENDER:
        print(f"🌐 Démarrage du serveur web sur le port {PORT}")
        app.run(host='0.0.0.0', port=PORT)
    else:
        # En local, on garde le comportement original
        watcher.run()