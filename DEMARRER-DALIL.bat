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
start "DALIL - API (codes SMS affiches ici)" /D "%~dp0backend" cmd /k .venv\Scripts\python -m uvicorn app.main:app --port 8000
start "DALIL - Site" /D "%~dp0frontend" cmd /k npm run dev

echo.
echo  Attente du demarrage du site...
set /a tries=0
:wait
set /a tries+=1
curl -s -o nul http://localhost:3000 && goto ready
if %tries% geq 90 goto ready
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
echo   Pour tout arreter : fermez les deux fenetres DALIL.
echo.
pause
