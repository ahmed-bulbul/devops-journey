#!/bin/bash
# GPG key setup for signed git commits
# Run this script to walk through the setup

set -e

echo "=== GPG Key Setup for Signed Commits ==="
echo ""

# 1. Check if GPG is installed
if ! command -v gpg &>/dev/null; then
    echo "[INFO] Installing gnupg..."
    sudo apt install -y gnupg
fi
echo "[OK] GPG version: $(gpg --version | head -1)"

# 2. List existing keys
echo ""
echo "=== Existing GPG keys ==="
gpg --list-secret-keys --keyid-format=long

# 3. Generate a new key (interactive)
echo ""
echo "=== Generating a new GPG key ==="
echo "When prompted:"
echo "  Key type: RSA and RSA (default)"
echo "  Key size: 4096"
echo "  Expiry: 1y (1 year)"
echo "  Name: Bulbul Ahmed"
echo "  Email: ahmedbulbul.cse@gmail.com"
echo ""
echo "Run this command:"
echo "  gpg --full-generate-key"
echo ""

# 4. Get key ID after generation
echo "=== After generating, get your key ID ==="
echo "  gpg --list-secret-keys --keyid-format=long"
echo "  # Look for line like: sec rsa4096/ABCD1234EFGH5678"
echo "  # Your key ID is: ABCD1234EFGH5678"
echo ""

# 5. Export public key for GitHub
echo "=== Export public key for GitHub ==="
echo "  gpg --armor --export YOUR_KEY_ID"
echo "  # Copy the output and paste in GitHub → Settings → SSH and GPG keys"
echo ""

# 6. Configure git to use GPG key
echo "=== Configure git to sign commits ==="
echo "  git config --global user.signingkey YOUR_KEY_ID"
echo "  git config --global commit.gpgsign true"
echo "  git config --global gpg.program gpg"
echo ""

# 7. Test signed commit
echo "=== Test signed commit ==="
echo "  git commit -m 'test: first signed commit'"
echo "  git log --show-signature -1"
echo ""

echo "=== Verify a signed commit ==="
echo "  git verify-commit HEAD"
