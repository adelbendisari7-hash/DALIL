@echo off
setlocal
chcp 65001 >nul
title DALIL - demarrage
cd /d "%~dp0"

rem ---------------------------------------------------------------------------
rem  Lance tout DALIL en un double-clic : API (port 8000) + site (port 3000).
rem  Votre numero de mobile ci-dessous devient administrateur a la 1re connexion.
rem ---------------------------------------------------------------------------
set "ADMIN_PHONE=0550000000"
rem  Modele de langage affine : DESACTIVE par defaut (decision du 17/11/2026). Sur ce portable il prend ~1 min
rem  par diagnostic (exigence : moins de 10 s) et ne gagne pas en precision (demo 88 -> 77 %, voir ml/README.md).
rem  Pour les mesures du memoire, mettre USE_LLM=1 (serveur llama.cpp, ~5 Go de memoire en q8_0).
set "USE_LLM=0"
rem  Site en version de production (construite au premier lancement et apres chaque modification, plus legere sur
rem  un telephone). SITE_DEV=1 : mode developpement, rechargement a chaud pendant qu'on modifie le site.
set "SITE_DEV=0"
set "LLM_GGUF=ml\artifacts\dalil-qwen3-4b-instruct-2507-q8_0.gguf"

echo.
echo  ===== DALIL : demarrage =====
echo.

where python >nul 2>nul || (echo [ERREUR] Python est introuvable. Installez Python 3.12 depuis python.org & pause & exit /b 1)
where npm >nul 2>nul || (echo [ERREUR] Node.js est introuvable. Installez Node.js depuis nodejs.org & pause & exit /b 1)

rem --- 1. Backend : environnement Python et dependances (la premiere fois seulement)
if not exist "backend\.venv\Scripts\python.exe" (
  echo [1/5] Creation de l'environnement Python...
  python -m venv backend\.venv || (echo [ERREUR] venv & pause & exit /b 1)
)
if not exist "backend\.venv\.deps-ok" (
  echo [1/5] Installation des dependances Python, quelques minutes...
  backend\.venv\Scripts\python -m pip install -q -r backend\requirements.txt || (echo [ERREUR] pip install & pause & exit /b 1)
  echo ok> "backend\.venv\.deps-ok"
) else (
  echo [1/5] Dependances Python deja installees
)

rem --- 2. Base de donnees : migrations + referentiels + magasins de demo (rejouables)
echo [2/5] Mise a jour de la base de donnees...
pushd backend
.venv\Scripts\python -m alembic upgrade head || (popd & echo [ERREUR] migrations & pause & exit /b 1)
.venv\Scripts\python -m app.seed || (popd & echo [ERREUR] chargement des referentiels & pause & exit /b 1)
popd

rem --- 3. Modele de diagnostic de reference (entraine une seule fois)
if not exist "ml\artifacts\baseline_tfidf_lr.joblib" (
  echo [3/5] Entrainement du modele de reference...
  backend\.venv\Scripts\python ml\train_baseline.py
) else (
  echo [3/5] Modele de diagnostic deja present
)

rem --- 4. Frontend : dependances Node (la premiere fois seulement)
if not exist "frontend\node_modules" (
  echo [4/5] Installation des dependances du site, quelques minutes...
  pushd frontend
  call npm install || (popd & echo [ERREUR] npm install & pause & exit /b 1)
  popd
) else (
  echo [4/5] Dependances du site deja installees
)

rem --- 5. Lancement dans deux fenetres (fermez-les pour tout arreter)
echo [5/5] Lancement de l'API et du site...
set "DALIL_ADMIN_PHONES=%ADMIN_PHONE%"
rem Recherche par vecteurs + reclassement (retombe sur les mots-cles si les modeles de ml\artifacts sont absents)
set "DALIL_RETRIEVAL_MODE=hybrid"
rem Classifieur a deux niveaux (24/11/2026) : les familles de pieces apprises sur L'Argus reclassent les pannes du
rem modele de reference (audit 82 -> 87 %, controle 88 -> 94 %, rien de perdu ailleurs). Fichier local, hors git :
rem python ml\train_family_reranker.py --alphas 0.25. Absent : modele de reference seul.
if exist "ml\artifacts\famille_rerank_a0.25.joblib" (
  set "DALIL_CLASSIFIER_PATH=%~dp0ml\artifacts\famille_rerank_a0.25.joblib"
  set "DALIL_MODEL_VERSION=tfidf-lr-reels-forums+familles-largus-techniconnexion-a0.25"
  echo      Classifieur a deux niveaux ^(familles apprises sur L'Argus et Techniconnexion^)
)
if not "%USE_LLM%"=="1" (
  echo      Diagnostic sans modele de langage ^(rapide ; USE_LLM=1 en haut de ce fichier pour l'activer^)
) else if exist "tools\llama.cpp\llama-server.exe" if exist "%LLM_GGUF%" (
  echo      Modele de langage affine : demarrage du serveur ^(port 8080^)
  start "DALIL - Modele de langage" /D "%~dp0" cmd /k tools\llama.cpp\llama-server.exe -m "%LLM_GGUF%" --port 8080 -c 4096 --alias dalil-lora --host 127.0.0.1
  set "DALIL_LLM_PROVIDER=openai_compat"
  set "DALIL_LLM_BASE_URL=http://127.0.0.1:8080/v1"
  set "DALIL_LLM_MODEL=dalil-lora"
  set "DALIL_LLM_TIMEOUT=300"
) else (
  echo      Modele de langage affine absent : diagnostic sans modele de langage
)
start "DALIL - API (codes SMS affiches ici)" /D "%~dp0backend" cmd /k .venv\Scripts\python -m uvicorn app.main:app --port 8000
if "%SITE_DEV%"=="1" (
  start "DALIL - Site" /D "%~dp0frontend" cmd /k npm run dev
) else (
  start "DALIL - Site" /D "%~dp0frontend" cmd /k "node scripts\build-si-besoin.mjs && npm run start"
)

echo.
echo  Attente du demarrage du site...
set /a tries=0
:wait
set /a tries+=1
curl -s -o nul http://localhost:3000 && goto ready
rem jusqu'a ~6 min : la premiere construction du site prend 1 a 3 minutes
if %tries% geq 180 goto ready
ping -n 3 127.0.0.1 >nul
goto wait

:ready
start "" http://localhost:3000
echo.
echo  ===== DALIL est lance =====
echo   Site           : http://localhost:3000
echo   API (doc)      : http://localhost:8000/docs
echo   Administrateur : connectez-vous avec le %ADMIN_PHONE%
echo   Le code SMS s'affiche dans la fenetre "DALIL - API".
echo   Pour tout arreter : fermez les fenetres DALIL (API, site, modele de langage).
rem Adresse du PC sur le Wi-Fi, pour ouvrir le site depuis un telephone (meme reseau)
set "LAN_IP="
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.PrefixOrigin -eq 'Dhcp' } | Select-Object -First 1).IPAddress"`) do set "LAN_IP=%%i"
if defined LAN_IP (
  echo.
  echo   Sur un telephone connecte au meme Wi-Fi : http://%LAN_IP%:3000
  echo   ^(si Windows demande d'autoriser Node.js sur le reseau prive, acceptez^)
)
echo.
pause
