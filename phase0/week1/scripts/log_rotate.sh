#!/bin/bash
# Script 2 — Log Rotator with Compression
# Usage: ./log_rotate.sh [log_dir] [max_keep]
#   log_dir   : directory containing *.log files (default: ../logs)
#   max_keep  : how many rotated archives to keep per log file (default: 5)

LOG_DIR="${1:-$(dirname "$0")/../logs}"
MAX_KEEP="${2:-5}"

LOG_DIR=$(realpath "$LOG_DIR")

if [ ! -d "$LOG_DIR" ]; then
    echo "ERROR: Log directory not found: $LOG_DIR"
    exit 1
fi

ARCHIVE_DIR="${LOG_DIR}/archive"
mkdir -p "$ARCHIVE_DIR"

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
ROTATED=0
SKIPPED=0

echo "============================================="
echo " Log Rotator"
echo " Directory : $LOG_DIR"
echo " Archive   : $ARCHIVE_DIR"
echo " Max Keep  : $MAX_KEEP per log file"
echo " Time      : $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================="
echo ""

# Rotate each .log file
while IFS= read -r logfile; do
    filename=$(basename "$logfile")
    base="${filename%.log}"

    if [ ! -s "$logfile" ]; then
        echo "  [SKIP] $filename — empty, nothing to rotate"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    archive_name="${base}_${TIMESTAMP}.log.gz"
    archive_path="${ARCHIVE_DIR}/${archive_name}"

    echo -n "  [ROTATE] $filename → archive/${archive_name} ... "
    if gzip -c "$logfile" > "$archive_path"; then
        # Truncate original without deleting (safe for running processes)
        > "$logfile"
        size=$(du -sh "$archive_path" | cut -f1)
        echo "done (${size})"
        ROTATED=$((ROTATED + 1))
    else
        echo "FAILED"
        rm -f "$archive_path"
    fi

    # Prune old archives for this log base name
    old_files=$(ls -t "${ARCHIVE_DIR}/${base}_"*.log.gz 2>/dev/null | tail -n +"$((MAX_KEEP + 1))")
    if [ -n "$old_files" ]; then
        echo "$old_files" | while IFS= read -r old; do
            echo "  [PURGE]  Removing old archive: $(basename "$old")"
            rm -f "$old"
        done
    fi

done < <(find "$LOG_DIR" -maxdepth 1 -name "*.log" -type f | sort)

echo ""
echo "  Rotated : $ROTATED file(s)"
echo "  Skipped : $SKIPPED file(s)"
echo ""
echo "  Archives in ${ARCHIVE_DIR}:"
ls -lh "${ARCHIVE_DIR}/" 2>/dev/null | awk 'NR>1 {printf "    %s  %s\n", $5, $9}'
echo "============================================="
