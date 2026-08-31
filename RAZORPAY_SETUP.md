# Razorpay integration — what changed & how to go live

## What changed
The old checkout was **fully simulated** (fake card fields, "Simulate Success/Failure"
buttons). It's now replaced with real Razorpay Checkout:

- `app/views.py` — `create_razorpay_order()`, `verify_razorpay_payment()`,
  `verify_razorpay_webhook_signature()`, and a new `razorpay_webhook` view.
- `app/models.py` — `Booking` now stores `razorpay_payment_id` alongside the
  existing `order_group_id` (holds the Razorpay order id).
- `app/urls.py` — new `razorpay-webhook/` endpoint.
- `templates/core/booking.html` — step 2 now loads Razorpay's `checkout.js`
  and opens the real payment modal instead of a fake card form.
- `carzo/settings.py` / `.env` — `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`,
  `RAZORPAY_WEBHOOK_SECRET` replace the old Cashfree settings.
- A migration (`app/migrations/0004_booking_razorpay_payment_id.py`) is included.

**How payment is verified (why this is "production level" and not just a demo):**
1. Server creates the Razorpay Order using the amount *you* calculated — never
   trusts an amount from the browser.
2. Razorpay Checkout opens in the browser, customer pays.
3. Browser gets back `razorpay_payment_id`, `razorpay_order_id`, `razorpay_signature`
   and POSTs them to your server.
4. **Server re-verifies the signature** (HMAC-SHA256 with your secret key)
   before creating the booking. Only then is the booking marked `paid`.
5. A webhook (`/razorpay-webhook/`) also listens directly from Razorpay's
   servers, so a booking still gets confirmed even if the customer's browser
   closes right after paying.

## 1. Get your Razorpay keys
1. Sign up / log in at https://dashboard.razorpay.com
2. Go to **Settings → API Keys** and generate a key pair.
   - While testing: use **Test Mode** keys (`rzp_test_...`).
   - To accept real money: complete Razorpay's KYC/business verification,
     switch to **Live Mode**, and generate live keys (`rzp_live_...`).
3. Go to **Settings → Webhooks**, add a webhook pointing to:
   `https://YOUR-DOMAIN/razorpay-webhook/`
   Subscribe to at least `payment.captured` and `payment.failed`.
   Copy the **webhook secret** shown there.

## 2. Fill in `.env`
```
RAZORPAY_KEY_ID=rzp_test_xxxxxxxx      # or rzp_live_xxxxxxxx when going live
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxxxxxxxxxxx
```
Never commit real keys to git — `.env` should already be in `.gitignore`.

## 3. Install & migrate
```
pip install -r requirements.txt
python manage.py migrate
```

## 4. Test it
Use Razorpay's test card `4111 1111 1111 1111`, any future expiry, any CVV,
OTP `1221` — full list at https://razorpay.com/docs/payments/payments/test-card-upi-details/

## 5. Before going fully live
- [ ] Complete Razorpay KYC and switch dashboard to Live Mode
- [ ] Replace test keys with live keys in your **production** environment's `.env`
- [ ] Set `DEBUG=False` and a real `SECRET_KEY` in production
- [ ] Set `ALLOWED_HOSTS` to your real domain
- [ ] Serve the whole app over **HTTPS** (Razorpay requires this in live mode)
- [ ] Deploy somewhere that runs Python/Django — **not GitHub Pages**, which
      only serves static files and can't run this backend or process payments
      securely at all.

## 6. Deploying on Render

The project now includes `build.sh` (installs deps, collects static files,
runs migrations) and is set up for Render's Postgres + gunicorn + whitenoise.

1. Push this project to a GitHub repo (`.env` stays out of git, it's already
   in `.gitignore`).
2. On Render: **New + → PostgreSQL** to create a database, copy its Internal
   Database URL.
3. **New + → Web Service**, connect the repo.
   - Build Command: `./build.sh`
   - Start Command: `gunicorn carzo.wsgi:application`
4. In the Web Service's **Environment** tab, add these (this is where all
   secrets live — never in the repo):
   - `SECRET_KEY` — a fresh random string, e.g. generate one with
     `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `your-app-name.onrender.com`
   - `DATABASE_URL` = the Internal Database URL from step 2
   - `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`
   - `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` if you use the email features
5. Deploy. Once live, update the webhook URL in the Razorpay dashboard to
   `https://your-app-name.onrender.com/razorpay-webhook/`.

**Known limitation:** uploaded car images (`MEDIA_ROOT`) are stored on local
disk, which Render wipes on every redeploy. Fine for testing; before real
users upload real car photos, move media storage to S3/Cloudflare R2 (e.g.
via `django-storages`).
