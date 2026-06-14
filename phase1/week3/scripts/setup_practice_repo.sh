#!/bin/bash
# Creates a practice git repository with realistic commit history
# for practicing rebase, cherry-pick, bisect, merge conflicts, etc.
#
# Run: bash scripts/setup_practice_repo.sh
# Creates: /tmp/git-practice/

set -e

REPO_DIR="/tmp/git-practice"

# Clean up if exists
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

git init
git config user.email "bulbul@devops.local"
git config user.name "Bulbul Ahmed"

echo "=== Setting up practice repository at $REPO_DIR ==="

# ─── Initial commit ───────────────────────────────────────────────────────────
mkdir -p src/main/java/com/example
cat > src/main/java/com/example/UserService.java << 'EOF'
public class UserService {
    public String getUser(int id) {
        return "user-" + id;
    }
}
EOF
git add .
git commit -m "feat(user): add UserService with getUser method"

# ─── Add more features ────────────────────────────────────────────────────────
cat > src/main/java/com/example/OrderService.java << 'EOF'
public class OrderService {
    public String createOrder(String userId) {
        return "order-for-" + userId;
    }
}
EOF
git add .
git commit -m "feat(order): add OrderService with createOrder method"

cat >> src/main/java/com/example/UserService.java << 'EOF'

    public void deleteUser(int id) {
        System.out.println("deleted: " + id);
    }
EOF
git add .
git commit -m "feat(user): add deleteUser method"

# ─── Introduce a bug (for bisect practice) ────────────────────────────────────
cat > src/main/java/com/example/UserService.java << 'EOF'
public class UserService {
    public String getUser(int id) {
        if (id < 0) return null;   // BUG: should throw exception
        return "user-" + id;
    }
    public void deleteUser(int id) {
        System.out.println("deleted: " + id);
    }
}
EOF
git add .
git commit -m "fix(user): add null check for negative id"

# ─── More commits after the bug ───────────────────────────────────────────────
echo "# Order Service" > README.md
git add .
git commit -m "docs: add README"

cat > src/main/java/com/example/ProductService.java << 'EOF'
public class ProductService {
    public String getProduct(int id) {
        return "product-" + id;
    }
}
EOF
git add .
git commit -m "feat(product): add ProductService"

echo "logging.level=INFO" > src/main/resources/application.properties
git add .
git commit -m "chore: add application.properties"

# ─── Create a feature branch for merge conflict practice ──────────────────────
git checkout -b feature/payment
cat > src/main/java/com/example/PaymentService.java << 'EOF'
public class PaymentService {
    public boolean processPayment(double amount) {
        return amount > 0;
    }
}
EOF
# Also modify UserService (will conflict with main branch change)
sed -i 's/return "user-" + id;/return "USER-" + id;  \/\/ capitalised/' \
    src/main/java/com/example/UserService.java
git add .
git commit -m "feat(payment): add PaymentService and update user format"

# ─── Back to main — make conflicting change ───────────────────────────────────
git checkout main
sed -i 's/return "user-" + id;/return "u-" + id;  \/\/ shortened/' \
    src/main/java/com/example/UserService.java
git add .
git commit -m "refactor(user): shorten user prefix"

echo ""
echo "=== Practice repo ready at: $REPO_DIR ==="
echo ""
echo "Git log:"
git log --oneline
echo ""
echo "Branches:"
git branch -a
echo ""
echo "Try these exercises:"
echo "  1. Merge feature/payment into main (will have a conflict!)"
echo "  2. git bisect to find when the null-return bug was introduced"
echo "  3. git rebase -i HEAD~3 to squash last 3 commits"
echo "  4. git cherry-pick a commit from feature/payment to main"
