#!/bin/bash
# Script 3 — Automated Backup
# Usage: ./backup.sh [source_dir] [backup_root] [max_backups]
#   source_dir   : what to back up (default: ../configs)
#   backup_root  : where to store backups (default: ../backup)
#   max_backups  : how many to keep before pruning (default: 5)

SOURCE_DIR="${1:-$(dirname "$0")/../configs}"
BACKUP_ROOT="${2:-$(dirname "$0")/../backup}"
MAX_BACKUPS="${3:-5}"

SOURCE_DIR=$(realpath "$SOURCE_DIR")
BACKUP_ROOT=$(realpath "$BACKUP_ROOT")

if [ ! -d "$SOURCE_DIR" ]; then
    echo "ERROR: Source directory not found: $SOURCE_DIR"
    exit 1
fi

mkdir -p "$BACKUP_ROOT"

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
ARCHIVE_NAME="backup_$(basename "$SOURCE_DIR")_${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="${BACKUP_ROOT}/${ARCHIVE_NAME}"
LOG_PATH="${BACKUP_ROOT}/backup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_PATH"
}

echo "============================================="
echo " Automated Backup"
echo " Source      : $SOURCE_DIR"
echo " Destination : $BACKUP_ROOT"
echo " Archive     : $ARCHIVE_NAME"
echo " Time        : $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================="
echo ""

log "START backup of $SOURCE_DIR"

# Count files being backed up
FILE_COUNT=$(find "$SOURCE_DIR" -type f | wc -l)
log "Files to back up: $FILE_COUNT"

# Create compressed archive
if tar -czf "$ARCHIVE_PATH" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")" 2>/dev/null; then
    SIZE=$(du -sh "$ARCHIVE_PATH" | cut -f1)
    log "SUCCESS: $ARCHIVE_NAME created (${SIZE}, ${FILE_COUNT} files)"
    echo ""
    echo "  [OK] Backup created: $ARCHIVE_PATH"
    echo "       Size   : $SIZE"
    echo "       Files  : $FILE_COUNT"
else
    log "FAILED: Could not create archive"
    echo ""
    echo "  [ERROR] Backup failed. Check $LOG_PATH"
    exit 1
fi

# Prune old backups beyond MAX_BACKUPS
echo ""
EXISTING=$(ls -t "${BACKUP_ROOT}"/backup_*.tar.gz 2>/dev/null)
TOTAL=$(echo "$EXISTING" | grep -c ".tar.gz" 2>/dev/null || echo 0)
echo "  Total backups: $TOTAL (max: $MAX_BACKUPS)"

OLD=$(ls -t "${BACKUP_ROOT}"/backup_*.tar.gz 2>/dev/null | tail -n +"$((MAX_BACKUPS + 1))")
if [ -n "$OLD" ]; then
    echo "$OLD" | while IFS= read -r old_file; do
        echo "  [PRUNE] Removing: $(basename "$old_file")"
        rm -f "$old_file"
        log "PRUNED: $(basename "$old_file")"
    done
fi

echo ""
echo "  Current backups:"
ls -lht "${BACKUP_ROOT}"/backup_*.tar.gz 2>/dev/null | awk '{printf "    %-40s %s\n", $9, $5}'

echo ""
log "END backup complete"
echo "============================================="
