# Dynamic QR Code Generator with PostgreSQL

A Flask-based web application that generates dynamic QR codes, allowing URL redirection updates without changing the QR image. Perfect for small businesses and personal use!


## 🔥 Features
- **Dynamic Redirection**: Update target URLs without regenerating QR codes
- **Database Backed**: PostgreSQL for reliable URL mapping
- **Instant Generation**: Create QR codes in <1 second
- **Free Hosting**: Designed for Render's free tier
- **Secure**: SHA-256 hashed QR identifiers

## 🛠 Tech Stack
- **Backend**: Python + Flask
- **Database**: PostgreSQL
- **QR Generation**: `qrcode` library
- **Hosting**: Render
- **Image Storage**: Server-side directory

## ⚙️ System Requirements
- Python 3.10+
- PostgreSQL 14+
- libzbar0 (for QR decoding)
- `pip` for package management

## 🚀 Installation

```bash
# Clone repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt