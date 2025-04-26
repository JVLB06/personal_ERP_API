from fastapi import FastAPI
from login import router as entrar
from secure import router as safe

app = FastAPI()

# Inclui os grupos de rotas no app
app.include_router(entrar)
app.include_router(safe)
