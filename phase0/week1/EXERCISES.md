# Week 1 — File System & Text Processing Exercises

Working directory: ~/workspace/aws-learn/phase0/week1/

Run all commands from this directory unless told otherwise.

---

## SECTION 1 — Navigating the File System

### 1.1 Basic Navigation
```bash
# See your current location
pwd

# List everything with details (size, permissions, date)
ls -lh

# List ALL files including hidden ones
ls -lha

# List only directories
ls -d */

# Go into logs folder and back
cd logs
pwd
cd ..
```

### 1.2 find — locate files by rules
```bash
# Find all .log files
find . -name "*.log"

# Find all .csv files
find . -name "*.csv"

# Find files larger than 1KB
find . -size +1k

# Find files modified in last 1 day
find . -mtime -1

# Find files by name pattern (case-insensitive)
find . -iname "*.properties"

# Find only directories
find . -type d

# Find and print full path
find . -name "*.log" -type f
```

**Challenge 1:** Find all files that contain the word "service" in their filename.
```bash
find . -name "*service*"
```

---

## SECTION 2 — cat, less, head, tail

```bash
# Print entire file
cat logs/app.log

# With line numbers
cat -n logs/app.log

# Read page by page (press q to quit, space for next page)
less logs/app.log

# First 10 lines
head logs/app.log

# First 5 lines
head -5 logs/app.log

# Last 10 lines
tail logs/app.log

# Last 20 lines
tail -20 logs/app.log

# VERY USEFUL — watch new lines being added in real time
tail -f logs/app.log
```

**Challenge 2:** Show only the last 5 lines of error.log
```bash
tail -5 logs/error.log
```

---

## SECTION 3 — grep — search inside files

```bash
# Find all ERROR lines in app.log
grep "ERROR" logs/app.log

# Find all WARN lines
grep "WARN" logs/app.log

# Case-insensitive search
grep -i "error" logs/app.log

# Show line numbers too
grep -n "ERROR" logs/app.log

# Count how many ERROR lines
grep -c "ERROR" logs/app.log

# Invert — show lines WITHOUT "INFO"
grep -v "INFO" logs/app.log

# Search in ALL log files at once
grep "ERROR" logs/*.log

# Search recursively in all files
grep -r "ERROR" logs/

# Show 2 lines BEFORE each match (context)
grep -B 2 "ERROR" logs/app.log

# Show 2 lines AFTER each match
grep -A 2 "ERROR" logs/app.log

# Show 2 lines before AND after
grep -C 2 "ERROR" logs/app.log

# Search for multiple patterns (OR)
grep -E "ERROR|WARN" logs/app.log

# Find lines matching a pattern with regex
grep -E "userId=[0-9]+" logs/app.log

# Find lines that start with a date
grep -E "^2026-06-01" logs/app.log
```

**Challenge 3:** Find all failed login attempts (lines with "Failed login")
```bash
grep "Failed login" logs/app.log
```

**Challenge 4:** Count total errors in error.log
```bash
grep -c "ERROR" logs/error.log
```

**Challenge 5:** Find all requests that returned status 500 in access.log
```bash
grep '" 500 ' logs/access.log
```

**Challenge 6:** Find all requests from suspicious IP 203.0.113.5
```bash
grep "203.0.113.5" logs/access.log
```

---

## SECTION 4 — cut — extract columns

```bash
# Extract column 1 from employees.csv (comma-separated)
cut -d',' -f1 data/employees.csv

# Extract name and department (columns 2 and 3)
cut -d',' -f2,3 data/employees.csv

# Extract from access.log — first column (IP address)
cut -d' ' -f1 logs/access.log

# Skip header line with tail
tail -n +2 data/employees.csv | cut -d',' -f2
```

**Challenge 7:** List all unique departments from employees.csv (no header)
```bash
tail -n +2 data/employees.csv | cut -d',' -f3
```

---

## SECTION 5 — sort and uniq — count and deduplicate

```bash
# Sort words.txt alphabetically
sort data/words.txt

# Sort in reverse
sort -r data/words.txt

# Remove duplicates (file must be sorted first!)
sort data/words.txt | uniq

# Count occurrences of each word
sort data/words.txt | uniq -c

# Sort by count (most frequent first)
sort data/words.txt | uniq -c | sort -rn

# Top 5 most used words
sort data/words.txt | uniq -c | sort -rn | head -5
```

**Challenge 8:** Count how many times each HTTP status code appears in access.log
```bash
awk '{print $9}' logs/access.log | sort | uniq -c | sort -rn
```

**Challenge 9:** Find which IP made the most requests in access.log
```bash
awk '{print $1}' logs/access.log | sort | uniq -c | sort -rn | head -3
```

---

## SECTION 6 — awk — column processing powerhouse

```bash
# Print column 1 of employees.csv (id)
awk -F',' '{print $1}' data/employees.csv

# Print name and salary
awk -F',' '{print $2, $4}' data/employees.csv

# Print formatted output
awk -F',' '{printf "Name: %-20s Salary: %s\n", $2, $4}' data/employees.csv

# Skip header row (NR = line number)
awk -F',' 'NR>1 {print $2, $3}' data/employees.csv

# Filter — print only Engineering employees
awk -F',' '$3=="Engineering" {print $2, $4}' data/employees.csv

# Condition — salary > 80000
awk -F',' 'NR>1 && $4+0 > 80000 {print $2, $3, $4}' data/employees.csv

# Sum all salaries
awk -F',' 'NR>1 {sum += $4} END {print "Total salary:", sum}' data/employees.csv

# Average salary
awk -F',' 'NR>1 {sum += $4; count++} END {print "Avg salary:", sum/count}' data/employees.csv

# Count employees per department
awk -F',' 'NR>1 {dept[$3]++} END {for (d in dept) print d, dept[d]}' data/employees.csv

# Max salary
awk -F',' 'NR>1 {if($4+0 > max) max=$4} END {print "Max salary:", max}' data/employees.csv
```

**Challenge 10:** Find the highest-paid employee (name and salary)
```bash
awk -F',' 'NR>1 {if($4+0 > max) {max=$4; name=$2}} END {print name, max}' data/employees.csv
```

**Challenge 11:** Print all active employees in Dhaka
```bash
awk -F',' 'NR>1 && $6=="Dhaka" && $7=="active" {print $2, $3}' data/employees.csv
```

---

## SECTION 7 — sed — find and replace in files

```bash
# Replace a word (print only, don't save)
sed 's/localhost/prod.db.internal/' configs/app.properties

# Replace globally (all occurrences on each line)
sed 's/localhost/prod.db.internal/g' configs/app.properties

# Save the change to file (in-place edit)
sed -i 's/development/production/' configs/app.properties
# CAREFUL: -i modifies the original file!

# Delete lines containing a pattern
sed '/^#/d' configs/app.properties

# Print only lines 5 to 10
sed -n '5,10p' configs/app.properties

# Print lines matching a pattern
sed -n '/spring.datasource/p' configs/app.properties

# Replace and save to new file
sed 's/debug-mode=false/debug-mode=true/' configs/app.properties > configs/app-debug.properties

# Delete blank lines
sed '/^$/d' configs/app.properties

# Add a prefix to each line
sed 's/^/   /' data/servers.txt
```

**Challenge 12:** Replace "password123" with "REDACTED" and save to a new file
```bash
sed 's/password123/REDACTED/' configs/app.properties > configs/app.safe.properties
```

**Challenge 13:** Extract only the property keys (left side of =) from app.properties
```bash
grep -v "^#" configs/app.properties | grep "=" | cut -d'=' -f1
```

---

## SECTION 8 — Pipe Chaining (combining commands)

This is where Linux power users live. Chain commands with | (pipe).

```bash
# How many unique IPs hit the API?
cut -d' ' -f1 logs/access.log | sort | uniq | wc -l

# Show only ERROR logs sorted by service name
grep "ERROR" logs/app.log | awk '{print $4, $0}' | sort

# Find the busiest minute in access.log
awk '{print $4}' logs/access.log | cut -d: -f1,2 | sort | uniq -c | sort -rn

# Which service threw the most errors?
grep "ERROR" logs/app.log | awk '{print $4}' | sort | uniq -c | sort -rn

# Average response time from access.log (last column)
awk '{sum+=$NF; count++} END {printf "Avg response: %.3fs\n", sum/count}' logs/access.log

# Find all 4xx and 5xx errors in access.log
awk '$9 >= 400 {print $1, $7, $9}' logs/access.log

# Count servers that are stopped
grep "stopped" data/servers.txt | wc -l

# List only running servers' IPs
awk '$3=="running" {print $2}' data/servers.txt
```

---

## SECTION 9 — File Operations (cp, mv, mkdir, rm)

```bash
# Copy a file
cp configs/app.properties backup/app.properties.bak

# Copy with verbose output
cp -v logs/app.log backup/

# Copy entire directory recursively
cp -r logs/ backup/logs-backup/

# Move (rename) a file
mv backup/app.properties.bak backup/app.properties.backup

# Create nested directories in one command
mkdir -p backup/2026/06/01

# Remove a file
rm backup/app.properties.backup

# Remove directory and contents (CAREFUL!)
rm -rf backup/2026/

# Check disk usage of each folder
du -sh */

# Check total disk used
df -h .
```

---

## SECTION 10 — wc — count lines, words, chars

```bash
# Count lines in app.log
wc -l logs/app.log

# Count words
wc -w logs/app.log

# Count characters
wc -c logs/app.log

# Count lines in all log files
wc -l logs/*.log

# Quick: how many employees in CSV? (minus header)
tail -n +2 data/employees.csv | wc -l
```

---

## REAL-WORLD CHALLENGES — DevOps Scenarios

These combine everything above. Try to solve without looking at the answer first!

### Challenge A — Security Audit
Find all IPs that got a 403 (Forbidden) response in access.log, count how many times each one hit, and show the top 3.
```bash
awk '$9==403 {print $1}' logs/access.log | sort | uniq -c | sort -rn | head -3
```

### Challenge B — Incident Report
From app.log, extract only ERROR and WARN lines, then show which service (column 4) had the most issues.
```bash
grep -E "ERROR|WARN" logs/app.log | awk '{print $4}' | sort | uniq -c | sort -rn
```

### Challenge C — Config Migration
Create a production config from app.properties by:
1. Replacing localhost with prod.internal
2. Changing debug-mode=false to debug-mode=false (already false, confirm)
3. Removing all comment lines (#)
4. Saving to configs/app-prod.properties
```bash
grep -v "^#" configs/app.properties \
  | sed 's/localhost/prod.internal/g' \
  | sed 's/development/production/' \
  > configs/app-prod.properties
```

### Challenge D — Salary Report
From employees.csv, print a report showing each department, number of employees, and total salary. Sort by total salary descending.
```bash
awk -F',' 'NR>1 && $7=="active" {dept[$3]++; sal[$3]+=$4} \
  END {for (d in dept) printf "%-15s %3d employees  Total: $%d\n", d, dept[d], sal[d]}' \
  data/employees.csv | sort -t'$' -k2 -rn
```

### Challenge E — Slow Request Finder
From access.log, find all requests that took more than 0.1 seconds (last column), show the URL and response time, sorted by slowest first.
```bash
awk '$NF > 0.1 {print $7, $NF}' logs/access.log | sort -k2 -rn
```

---

## QUICK REFERENCE CARD

| Command | What it does |
|---------|-------------|
| `grep "text" file` | Find lines containing "text" |
| `grep -n` | Show line numbers |
| `grep -c` | Count matching lines |
| `grep -v` | Invert — lines NOT matching |
| `grep -r` | Search recursively |
| `grep -E` | Extended regex (use \|for OR) |
| `awk '{print $1}'` | Print column 1 |
| `awk -F','` | Use comma as separator |
| `awk 'NR>1'` | Skip first line (header) |
| `awk 'END{}'` | Run after all lines processed |
| `sed 's/a/b/'` | Replace first a with b per line |
| `sed 's/a/b/g'` | Replace ALL a with b |
| `sed -i` | Edit file in-place |
| `cut -d',' -f2` | Get column 2 (comma-delimited) |
| `sort \| uniq -c` | Count occurrences |
| `sort -rn` | Sort numeric, descending |
| `wc -l` | Count lines |
| `head -n` | First n lines |
| `tail -n` | Last n lines |
| `tail -f` | Follow file (real-time) |
| `find . -name "*.log"` | Find files by name pattern |

---

## DONE? Checklist

- [ ] I can navigate directories with ls, cd, pwd
- [ ] I can use find to locate files by name, size, date
- [ ] I can search inside files with grep (including -n, -c, -v, -E)
- [ ] I can extract columns with cut and awk
- [ ] I can count/deduplicate with sort | uniq -c
- [ ] I can find-and-replace with sed
- [ ] I can chain 3+ commands with pipes
- [ ] I completed all 5 Real-World Challenges

Next: Section 2 — Process Management (ps, htop, systemctl)
