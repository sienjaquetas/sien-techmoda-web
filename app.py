from flask import Flask, render_template, request, redirect
from datetime import datetime
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def criar_tabelas():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            numero VARCHAR(20),
            filial VARCHAR(100),
            cliente VARCHAR(100),
            modelo VARCHAR(100),
            costureira VARCHAR(100),
            data_saida DATE,
            data_retorno DATE,
            status VARCHAR(20)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

criar_tabelas()

@app.route("/")
def dashboard():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM pedidos ORDER BY id DESC")
    dados = cur.fetchall()

    cur.close()
    conn.close()

    pedidos = []
    atrasados = 0
    hoje = datetime.now().date()

    for p in dados:
        data_retorno = p[7]
        status = p[8]

        if data_retorno and data_retorno < hoje and status != "PAGO":
            atrasados += 1

        pedidos.append({
            "numero": p[1],
            "filial": p[2],
            "cliente": p[3],
            "modelo": p[4],
            "costureira": p[5],
            "data_retorno": p[7],
            "status": p[8]
        })

    return render_template(
        "dashboard.html",
        pedidos=pedidos,
        total=len(pedidos),
        atrasados=atrasados
    )

@app.route("/novo", methods=["POST"])
def novo():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM pedidos")
    total = cur.fetchone()[0] + 1
    numero = f"PED-{str(total).zfill(4)}"

    cur.execute("""
        INSERT INTO pedidos
        (numero, filial, cliente, modelo, costureira, data_saida, data_retorno, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        numero,
        request.form["filial"],
        request.form["cliente"],
        request.form["modelo"],
        request.form["costureira"],
        request.form["data_saida"] or None,
        request.form["data_retorno"] or None,
        "ABERTO"
    ))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")

@app.route("/pagar/<numero>")
def pagar(numero):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE pedidos SET status='PAGO' WHERE numero=%s", (numero,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
