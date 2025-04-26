# personal_ERP_API
API que funciona como um ERP pessoal, auxiliando o usuário a manejar seu patrimônio, com sugestões de medidas e retornos de informações essenciais, apresentados em um modelo de CRUD. 
Pode rodar a API direto no local do arquivo ativando o VENV e usando o Uvicorn para inicializar a API. Seguem os comandos

erp/Scripts/activate
uvicorn main:app --host 0.0.0.0 --port 5000 --reload

Use CNTRL + C para parar a API. Para acessar a API pode utilizar o IP local da máquina onde ela está hospedada e para abrir a documentação basta adicionar a route /docs
