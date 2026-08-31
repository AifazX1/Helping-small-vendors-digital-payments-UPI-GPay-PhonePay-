import streamlit as st
import random
from datetime import datetime
import qrcode
import html
from io import BytesIO

st.set_page_config(
    page_title="VendorPay — Digital Payment Demo",
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- State ----------
if "history" not in st.session_state:
    st.session_state.history = [
        {
            "id": "VP-DEMO-1001",
            "customer": "Demo Customer",
            "amount": 250.00,
            "status": "Success",
            "method": "UPI / QR",
        }
    ]

if "page" not in st.session_state:
    st.session_state.page = "payment"

if "gateway_open" not in st.session_state:
    st.session_state.gateway_open = False

if "result" not in st.session_state:
    st.session_state.result = None

if "amount" not in st.session_state:
    st.session_state.amount = 250.0

# ---------- Styling ----------
st.markdown("""
<style>
:root{
  --bg:#07111f; --card:rgba(15,27,47,.82); --line:rgba(255,255,255,.1);
  --text:#f5f7fb; --muted:#9eabc0; --accent:#62e6b4; --blue:#6aa7ff;
  --danger:#ff6b7a; --warning:#ffd166;
}
.stApp{
  color:var(--text);
  background:
    radial-gradient(circle at 10% 10%,rgba(98,230,180,.14),transparent 30%),
    radial-gradient(circle at 90% 15%,rgba(106,167,255,.18),transparent 28%),
    linear-gradient(135deg,#06101d,#0b1425 55%,#081321);
}
.block-container{max-width:1180px;padding-top:1.2rem;padding-bottom:2rem}
.brand{display:flex;gap:12px;align-items:center}
.logo{
 width:44px;height:44px;border-radius:14px;display:grid;place-items:center;
 background:linear-gradient(135deg,#62e6b4,#4bb5ff);color:#06111c;
 font-weight:900;font-size:22px;padding:10px
}
.brand h1{font-size:18px;margin:0}.brand small{color:#9eabc0}
.badge{border:1px solid rgba(255,255,255,.1);padding:8px 12px;border-radius:999px;color:#b8c5d9;font-size:12px}
.card{
 background:rgba(15,27,47,.82);border:1px solid rgba(255,255,255,.1);
 border-radius:28px;box-shadow:0 25px 70px rgba(0,0,0,.35);
 padding:28px
}
.left-card{min-height:440px}
.kicker{color:#62e6b4;font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase}
.hero-title{font-size:42px;line-height:1.03;margin:12px 0 14px;letter-spacing:-1.5px;font-weight:800}
.lead{color:#b8c5d9;line-height:1.7}
.vendor{
 margin-top:25px;padding:16px;border:1px solid rgba(255,255,255,.1);border-radius:18px;
 display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,.035)
}
.vendor span{font-size:12px;color:#9eabc0;display:block}
.status{display:flex;align-items:center;gap:7px;color:#62e6b4;font-size:12px}
.dot{width:8px;height:8px;border-radius:50%;background:#62e6b4;box-shadow:0 0 14px #62e6b4}
.feature{
 padding:18px;border-radius:20px;border:1px solid rgba(255,255,255,.1);
 background:rgba(255,255,255,.025);height:100%
}
.feature b{display:block;margin:8px 0 5px}.feature p{font-size:12px;color:#9eabc0;line-height:1.55;margin:0}
.amount-label{color:#9eabc0;font-size:13px}.amount{font-size:50px;font-weight:850;margin:3px 0 22px}
.demo-note{font-size:11px;color:#7f8da2;text-align:center;margin-top:11px}
.section-card{
 margin-top:22px;padding:22px;background:rgba(15,27,47,.82);
 border:1px solid rgba(255,255,255,.1);border-radius:28px
}
.receipt{
 margin:18px 0;padding:15px;border-radius:16px;background:#0a1728;
 border:1px solid rgba(255,255,255,.1);text-align:left
}
.receipt-row{display:flex;justify-content:space-between;padding:6px 0;color:#aebbd0;font-size:13px}
.receipt strong{color:#eef3fa}
.success{color:#62e6b4}.failed{color:#ff6b7a}
.result-icon{font-size:64px;text-align:center}
.result-title{text-align:center;font-size:27px;margin:4px 0 7px}
.result-text{text-align:center;color:#9eabc0;line-height:1.6}
.qrbox{
 width:225px;height:225px;margin:14px auto;padding:14px;border-radius:20px;
 background:white;display:flex;align-items:center;justify-content:center;
 box-shadow:0 15px 45px rgba(0,0,0,.3)
}
.method{
 padding:12px;border:1px solid rgba(255,255,255,.1);border-radius:14px;
 background:#0b182a;color:#cbd7e8;text-align:center
}
.timer{text-align:center;font-size:13px;color:#ffd166;margin:10px 0 18px}
footer{text-align:center;color:#65758c;font-size:11px;margin-top:25px}
div[data-testid="stButton"] button{
 border-radius:14px;font-weight:800;min-height:46px
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:28px">
  <div class="brand">
    <div class="logo">₹</div>
    <div><h1>VendorPay</h1><small>Digital payment demo</small></div>
  </div>
  <div class="badge">LOCALHOST • PROJECT DEMO</div>
</div>
""", unsafe_allow_html=True)

# ---------- Gateway / Result ----------
if st.session_state.gateway_open:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    result = st.session_state.result

    if result:
        success = result["success"]
        icon = "✓" if success else "×"
        title = "Payment Successful" if success else "Payment Failed"
        result_title = "Payment received" if success else "Transaction unsuccessful"
        msg = result["message"]

        st.markdown(
            f'<div class="result-icon {"success" if success else "failed"}">{icon}</div>'
            f'<div class="kicker" style="text-align:center">{title}</div>'
            f'<div class="result-title">{result_title}</div>'
            f'<p class="result-text">{html.escape(msg)}</p>',
            unsafe_allow_html=True
        )

        method = result["method"]
        st.markdown(f"""
        <div class="receipt">
          <div class="receipt-row"><span>Transaction ID</span><strong>{result["id"]}</strong></div>
          <div class="receipt-row"><span>Customer</span><strong>{html.escape(result["customer"])}</strong></div>
          <div class="receipt-row"><span>Vendor</span><strong>Shree Ganesh Store</strong></div>
          <div class="receipt-row"><span>Amount</span><strong>₹{result["amount"]:.2f}</strong></div>
          <div class="receipt-row"><span>Mode</span><strong>{html.escape(method)}</strong></div>
          <div class="receipt-row"><span>Status</span><strong class="{"success" if success else "failed"}">{result["status"].upper()}</strong></div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Close", use_container_width=True):
                st.session_state.gateway_open = False
                st.session_state.result = None
                st.rerun()
        with c2:
            if st.button("New Payment", type="primary", use_container_width=True):
                st.session_state.result = None
                st.rerun()

        st.markdown('<div class="demo-note">SIMULATION • No money was transferred</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="kicker" style="text-align:center">Secure Demo Checkout</div><h2 style="text-align:center">Scan & Pay</h2>', unsafe_allow_html=True)

        # Decorative QR; deliberately not a real UPI URI, matching the original HTML.
        qr_payload = f"VENDORPAY-DEMO|{st.session_state.customer if 'customer' in st.session_state else 'Demo Customer'}|{st.session_state.amount:.2f}"
        qr = qrcode.QRCode(version=2, box_size=7, border=2)
        qr.add_data(qr_payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#07111f", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.markdown('<div class="qrbox">', unsafe_allow_html=True)
        st.image(buf.getvalue(), width=195)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div style="text-align:center;color:#b9c5d7;font-size:13px">Demo UPI ID: <strong>vendorpay.demo@upi</strong></div>', unsafe_allow_html=True)
        st.markdown('<div class="timer">Payment window: <strong>01:00</strong></div>', unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        with m1:
            st.markdown('<div class="method">UPI / QR</div>', unsafe_allow_html=True)
        with m2:
            st.markdown('<div class="method">App Simulation</div>', unsafe_allow_html=True)

        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Simulate Successful Payment", type="primary", use_container_width=True):
                txid = f"VP-{random.randint(100000,999999)}"
                customer = st.session_state.customer
                item = {"id":txid,"customer":customer,"amount":st.session_state.amount,
                        "status":"Success","method":st.session_state.method}
                st.session_state.history.insert(0, item)
                st.session_state.result = {
                    **item, "success": True,
                    "message":"The demo transaction was successfully processed."
                }
                st.rerun()
        with c2:
            if st.button("Simulate Failed Payment", use_container_width=True):
                txid = f"VP-{random.randint(100000,999999)}"
                customer = st.session_state.customer
                item = {"id":txid,"customer":customer,"amount":st.session_state.amount,
                        "status":"Failed","method":st.session_state.method}
                st.session_state.history.insert(0, item)
                st.session_state.result = {
                    **item, "success": False,
                    "message":"The demo payment could not be completed."
                }
                st.rerun()

        st.markdown('<div class="demo-note">For presentation/testing only. No actual transaction occurs.</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("← Back to Payment Form"):
        st.session_state.gateway_open = False
        st.session_state.result = None
        st.rerun()

else:
    # ---------- Main payment form ----------
    left, right = st.columns([1.1, .9], gap="medium")

    with left:
        st.markdown("""
        <div class="card left-card">
          <div class="kicker">Helping Small Vendors Go Digital</div>
          <div class="hero-title">Simple. Fast.<br>Digital payments.</div>
          <p class="lead">A realistic-looking payment gateway demonstration designed for your Community Engagement Project. It shows how a small vendor can collect a UPI payment using a QR code, wait for confirmation, and receive a success or failed result.</p>
          <div class="vendor">
            <div><strong>Shree Ganesh General Store</strong><span>Small Vendor • Digital Payment Enabled</span></div>
            <div class="status"><span class="dot"></span>Online</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown('<div class="feature"><div style="font-size:22px">▦</div><b>QR Payment</b><p>Customer can scan the demo QR code.</p></div>', unsafe_allow_html=True)
        with f2:
            st.markdown('<div class="feature"><div style="font-size:22px">⏱</div><b>Live Timer</b><p>Simulated gateway processing and expiry.</p></div>', unsafe_allow_html=True)
        with f3:
            st.markdown('<div class="feature"><div style="font-size:22px">✓</div><b>Verification</b><p>Success and failed states for presentation.</p></div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="amount-label">Amount to pay</div>', unsafe_allow_html=True)

        customer = st.text_input("Customer Name", value="Demo Customer")
        amount = st.number_input("Amount (₹)", min_value=1.0, value=float(st.session_state.amount), step=10.0)
        method = st.selectbox("Payment Method", ["UPI / QR", "Paytm", "Google Pay"])

        st.session_state.customer = customer.strip() or "Demo Customer"
        st.session_state.amount = amount
        st.session_state.method = method

        st.markdown(f'<div class="amount">₹{amount:,.2f}</div>', unsafe_allow_html=True)

        if st.button("Proceed to Payment →", type="primary", use_container_width=True):
            st.session_state.gateway_open = True
            st.session_state.result = None
            st.rerun()

        st.markdown('<div class="demo-note">Demo only • No real money is transferred</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- History ----------
st.markdown('<div class="section-card"><h3>Demo Transaction History</h3>', unsafe_allow_html=True)

rows = ""
for x in st.session_state.history:
    cls = "success" if x["status"] == "Success" else "failed"
    rows += f"""
    <tr>
      <td>{html.escape(x["id"])}</td>
      <td>{html.escape(x["customer"])}</td>
      <td>₹{x["amount"]:.2f}</td>
      <td><span class="pill {cls}">{x["status"]}</span></td>
    </tr>
    """

st.markdown(f"""
<style>
.history-table{{width:100%;border-collapse:collapse;font-size:13px}}
.history-table th,.history-table td{{text-align:left;padding:11px 8px;border-bottom:1px solid rgba(255,255,255,.1);color:#b9c5d7}}
.history-table th{{color:#fff}}
.pill{{padding:5px 9px;border-radius:999px;font-size:11px}}
.pill.success{{background:rgba(98,230,180,.1);color:#62e6b4}}
.pill.failed{{background:rgba(255,107,122,.1);color:#ff6b7a}}
</style>
<table class="history-table">
<thead><tr><th>Transaction</th><th>Customer</th><th>Amount</th><th>Status</th></tr></thead>
<tbody>{rows}</tbody>
</table>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<footer>VendorPay is a simulated localhost payment gateway for academic demonstration.
It is not connected to UPI, Paytm, Google Pay, a bank, or any payment processor.</footer>
""", unsafe_allow_html=True)
