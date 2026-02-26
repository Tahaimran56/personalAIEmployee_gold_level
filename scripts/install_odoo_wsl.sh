#!/bin/bash
# Odoo 19 Installation Script for WSL Ubuntu
# Gold Tier AI Employee - Accounting Integration

set -e  # Exit on error

echo "=========================================="
echo "Odoo 19 Installation for WSL Ubuntu"
echo "Gold Tier AI Employee Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Update system
echo -e "${YELLOW}Step 1: Updating system packages...${NC}"
sudo apt update
sudo apt upgrade -y

# Step 2: Install PostgreSQL
echo -e "${YELLOW}Step 2: Installing PostgreSQL...${NC}"
sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL
echo -e "${YELLOW}Starting PostgreSQL service...${NC}"
sudo service postgresql start

# Create Odoo database user
echo -e "${YELLOW}Creating Odoo database user...${NC}"
sudo -u postgres psql -c "DROP USER IF EXISTS odoo;"
sudo -u postgres psql -c "CREATE USER odoo WITH CREATEDB PASSWORD 'odoo';"
echo -e "${GREEN}✓ PostgreSQL user 'odoo' created${NC}"

# Step 3: Install Python and dependencies
echo -e "${YELLOW}Step 3: Installing Python dependencies...${NC}"
sudo apt install -y python3-pip python3-dev python3-venv \
  libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev \
  libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
  libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev \
  libfribidi-dev libxcb1-dev libpq-dev

# Step 4: Install wkhtmltopdf (for PDF reports)
echo -e "${YELLOW}Step 4: Installing wkhtmltopdf...${NC}"
sudo apt install -y wkhtmltopdf

# Step 5: Install Node.js (for assets)
echo -e "${YELLOW}Step 5: Installing Node.js...${NC}"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
    sudo apt install -y nodejs
fi
echo -e "${GREEN}✓ Node.js $(node --version) installed${NC}"

# Step 6: Clone Odoo 19
echo -e "${YELLOW}Step 6: Cloning Odoo 19 from GitHub...${NC}"
cd ~
if [ -d "odoo19" ]; then
    echo -e "${YELLOW}Odoo directory exists, removing...${NC}"
    rm -rf odoo19
fi
git clone https://github.com/odoo/odoo.git --depth 1 --branch 19.0 odoo19
cd odoo19

# Step 7: Install Python requirements
echo -e "${YELLOW}Step 7: Installing Odoo Python requirements...${NC}"
pip3 install -r requirements.txt

# Step 8: Create Odoo configuration
echo -e "${YELLOW}Step 8: Creating Odoo configuration...${NC}"
mkdir -p ~/.odoo
cat > ~/.odoo/odoo.conf << 'EOF'
[options]
admin_passwd = admin123
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
addons_path = ~/odoo19/addons
xmlrpc_port = 8069
logfile = ~/.odoo/odoo.log
log_level = info
EOF

echo -e "${GREEN}✓ Configuration created at ~/.odoo/odoo.conf${NC}"

# Step 9: Create startup script
echo -e "${YELLOW}Step 9: Creating startup script...${NC}"
cat > ~/start-odoo.sh << 'EOF'
#!/bin/bash
# Start Odoo 19 for Gold Tier AI Employee

echo "Starting PostgreSQL..."
sudo service postgresql start

echo "Starting Odoo 19..."
cd ~/odoo19
python3 odoo-bin -c ~/.odoo/odoo.conf
EOF

chmod +x ~/start-odoo.sh
echo -e "${GREEN}✓ Startup script created at ~/start-odoo.sh${NC}"

# Step 10: Create stop script
cat > ~/stop-odoo.sh << 'EOF'
#!/bin/bash
# Stop Odoo 19

echo "Stopping Odoo..."
pkill -f "python3 odoo-bin"
echo "Odoo stopped"
EOF

chmod +x ~/stop-odoo.sh
echo -e "${GREEN}✓ Stop script created at ~/stop-odoo.sh${NC}"

# Step 11: Auto-start PostgreSQL on WSL boot
echo -e "${YELLOW}Step 10: Configuring PostgreSQL auto-start...${NC}"
if ! grep -q "sudo service postgresql start" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Auto-start PostgreSQL for Odoo" >> ~/.bashrc
    echo "sudo service postgresql start > /dev/null 2>&1" >> ~/.bashrc
    echo -e "${GREEN}✓ PostgreSQL will auto-start on WSL boot${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Odoo 19 Installation Complete!${NC}"
echo "=========================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Start Odoo:"
echo "   ~/start-odoo.sh"
echo ""
echo "2. Access Odoo in your browser:"
echo "   http://localhost:8069"
echo ""
echo "3. Create database:"
echo "   - Master Password: admin123"
echo "   - Database Name: gold_tier_accounting"
echo "   - Email: admin"
echo "   - Password: admin (change this!)"
echo ""
echo "4. Update your .env file with:"
echo "   ODOO_URL=http://localhost:8069"
echo "   ODOO_DATABASE=gold_tier_accounting"
echo "   ODOO_USERNAME=admin"
echo "   ODOO_PASSWORD=your_password"
echo ""
echo "To stop Odoo: ~/stop-odoo.sh"
echo ""
