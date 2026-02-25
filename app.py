from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

pedidos = []

@app.route("/")
def dashboard():
    total_pedidos = len(pedidos)
    atrasados = 0

    hoje = datetime.now().date()

    for p in pedidos:
        if p["data_retorno"]:
            data_ret = datetime.strptime(p["data_retorno"], "%Y-%m-%d").date()
            if data_ret < hoje and p["status"] != "PAGO":
                atrasados += 1

    return render_template(
        "dashboard.html",
        total_pedidos=total_pedidos,
        atrasados=atrasados,
        pedidos=pedidos
    )

@app.route("/novo", methods=["POST"])
def novo_pedido():
    numero = f"PED-{str(len(pedidos)+1).zfill(4)}"

    pedidos.append({
        "numero": numero,
        "cliente": request.form["cliente"],
        "modelo": request.form["modelo"],
        "costureira": request.form["costureira"],
        "data_saida": request.form["data_saida"],
        "data_retorno": request.form["data_retorno"],
        "status": "ABERTO"
    })

    return redirect("/")

@app.route("/pagar/<numero>")
def pagar(numero):
    for p in pedidos:
        if p["numero"] == numero:
            p["status"] = "PAGO"
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
