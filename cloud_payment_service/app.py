
# -*- coding: utf-8 -*-
"""
cloud_payment_service_v1
云端模拟支付回调服务：用于 QSM368ZP-WF 智能零售终端比赛演示。
运行：python3 app.py
"""

import csv
import io
import json
import os
import sqlite3
import time
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, Response, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "cloud_payment.db"
SERVICE_NAME = "QSM368ZP Cloud Payment Service"

app = Flask(__name__)
app.secret_key = "qsm-cloud-payment-demo"


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS cloud_orders (
        cloud_order_id TEXT PRIMARY KEY,
        terminal_id TEXT,
        local_order_id TEXT,
        total_price_cent INTEGER NOT NULL,
        currency TEXT DEFAULT 'CNY',
        status TEXT DEFAULT 'waiting_payment',
        items_json TEXT,
        created_at TEXT,
        paid_at TEXT,
        client_ip TEXT,
        user_agent TEXT
    );

    CREATE TABLE IF NOT EXISTS cloud_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cloud_order_id TEXT,
        event_type TEXT,
        status TEXT,
        message TEXT,
        created_at TEXT,
        payload TEXT
    );
    """)
    conn.commit()
    conn.close()


def money(cents):
    return f"¥{int(cents or 0) / 100:.2f}"


def log_event(cloud_order_id, event_type, status=None, message="", payload=None):
    conn = db()
    conn.execute("""
        INSERT INTO cloud_events(cloud_order_id,event_type,status,message,created_at,payload)
        VALUES(?,?,?,?,?,?)
    """, (cloud_order_id, event_type, status, message, now_str(), json.dumps(payload or {}, ensure_ascii=False)))
    conn.commit()
    conn.close()


def mark_order_paid(cloud_order_id, method="POST"):
    paid_at = now_str()
    conn = db()
    order = conn.execute("SELECT * FROM cloud_orders WHERE cloud_order_id=?", (cloud_order_id,)).fetchone()
    if not order:
        conn.close()
        return None
    before_status = order["status"]
    if before_status != "paid":
        conn.execute(
            "UPDATE cloud_orders SET status='paid', paid_at=? WHERE cloud_order_id=?",
            (paid_at, cloud_order_id),
        )
        conn.commit()
    refreshed = conn.execute("SELECT * FROM cloud_orders WHERE cloud_order_id=?", (cloud_order_id,)).fetchone()
    conn.close()
    log_event(
        cloud_order_id,
        "mock_pay_success",
        "paid",
        "mobile clicked mock pay success",
        {"method": method, "status_before": before_status, "status_after": "paid"},
    )
    return refreshed


def base_url():
    # request.host_url includes trailing slash
    return request.host_url.rstrip("/")


@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/health")
def health():
    return jsonify({"ok": True, "service": SERVICE_NAME, "time": now_str()})


@app.route("/api/orders", methods=["POST"])
def api_create_order():
    data = request.get_json(force=True, silent=True) or {}
    total_price_cent = int(data.get("total_price_cent") or 0)
    local_order_id = data.get("local_order_id") or ""
    terminal_id = data.get("terminal_id") or "unknown-terminal"
    items = data.get("items") or []
    if total_price_cent <= 0:
        return jsonify({"ok": False, "error": "invalid_total"}), 400

    cloud_order_id = "CLOUD" + datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:6].upper()
    pay_url = f"{base_url()}/pay/{cloud_order_id}"
    conn = db()
    conn.execute("""
        INSERT INTO cloud_orders(cloud_order_id,terminal_id,local_order_id,total_price_cent,currency,status,
                                 items_json,created_at,paid_at,client_ip,user_agent)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)
    """, (cloud_order_id, terminal_id, local_order_id, total_price_cent, data.get("currency", "CNY"),
          "waiting_payment", json.dumps(items, ensure_ascii=False), now_str(), None,
          request.remote_addr, request.headers.get("User-Agent", "")))
    conn.commit()
    conn.close()
    log_event(cloud_order_id, "create_order", "waiting_payment", "cloud order created", data)
    return jsonify({
        "ok": True,
        "cloud_order_id": cloud_order_id,
        "local_order_id": local_order_id,
        "status": "waiting_payment",
        "cloud_pay_url": pay_url,
        "pay_url": pay_url,
        "created_at": now_str(),
    })


@app.route("/api/orders/<cloud_order_id>")
def api_order_status(cloud_order_id):
    conn = db()
    order = conn.execute("SELECT * FROM cloud_orders WHERE cloud_order_id=?", (cloud_order_id,)).fetchone()
    conn.close()
    if not order:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({
        "ok": True,
        "cloud_order_id": order["cloud_order_id"],
        "local_order_id": order["local_order_id"],
        "terminal_id": order["terminal_id"],
        "total_price_cent": order["total_price_cent"],
        "status": order["status"],
        "created_at": order["created_at"],
        "paid_at": order["paid_at"],
    })


@app.route("/pay/<cloud_order_id>", methods=["GET", "POST"])
def pay_page(cloud_order_id):
    conn = db()
    order = conn.execute("SELECT * FROM cloud_orders WHERE cloud_order_id=?", (cloud_order_id,)).fetchone()
    if not order:
        conn.close()
        return "云端订单不存在", 404
    items = json.loads(order["items_json"] or "[]")
    if request.method == "POST":
        conn.close()
        mark_order_paid(cloud_order_id, method=request.method)
        return redirect(url_for("pay_success_page", cloud_order_id=cloud_order_id))
    conn.close()
    return render_template("pay.html", order=order, items=items, money=money)


@app.route("/pay/<cloud_order_id>/success", methods=["GET", "POST"])
def pay_success_page(cloud_order_id):
    order = mark_order_paid(cloud_order_id, method=request.method)
    if not order:
        return "云端订单不存在", 404
    return render_template("pay_success.html", order=order, money=money, paid_at=order["paid_at"] or now_str())


@app.route("/dashboard")
def dashboard():
    conn = db()
    orders = conn.execute("SELECT * FROM cloud_orders ORDER BY created_at DESC LIMIT 100").fetchall()
    events = conn.execute("SELECT * FROM cloud_events ORDER BY event_id DESC LIMIT 100").fetchall()
    total = conn.execute("SELECT COUNT(*) AS n, COALESCE(SUM(total_price_cent),0) AS amount FROM cloud_orders").fetchone()
    paid = conn.execute("SELECT COUNT(*) AS n, COALESCE(SUM(total_price_cent),0) AS amount FROM cloud_orders WHERE status='paid'").fetchone()
    conn.close()
    return render_template("dashboard.html", orders=orders, events=events, total=total, paid=paid, money=money)


@app.route("/export/orders.csv")
def export_orders():
    conn = db()
    rows = conn.execute("SELECT * FROM cloud_orders ORDER BY created_at DESC").fetchall()
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["cloud_order_id","terminal_id","local_order_id","total_price_cent","status","created_at","paid_at","client_ip"])
    for r in rows:
        w.writerow([r["cloud_order_id"], r["terminal_id"], r["local_order_id"], r["total_price_cent"], r["status"], r["created_at"], r["paid_at"], r["client_ip"]])
    conn.close()
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=cloud_orders.csv"})


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
