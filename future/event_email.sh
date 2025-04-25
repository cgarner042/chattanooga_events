#!/bin/bash
# Email both XLSX and CSV files with recipient selection

source ~/.profile

# Config
CSV_FILE="$HOME/code/chattanooga_events/data/all_events.csv"
XLSX_FILE="$HOME/code/chattanooga_events/data/all_events.xlsx"
SUBJECT="Chattanooga Events $(date +'%Y-%m-%d')"
BODY="Attached:
- Primary Data (XLSX)
- Backup CSV copy"

# Preset recipients (Edit these!)
recipients=(
    "work@example.com:Work Account"
    "personal@gmail.com:Personal Gmail"
    "team@org.org:Project Team"
    "backup@example.com:Backup Address"
)

# Validate files
missing_files=()
[ ! -f "$CSV_FILE" ] && missing_files+=("$(basename "$CSV_FILE")")
[ ! -f "$XLSX_FILE" ] && missing_files+=("$(basename "$XLSX_FILE")")

if [ ${#missing_files[@]} -gt 0 ]; then
    notify-send "Error" "Missing files:\n${missing_files[*]}"
    exit 1
fi

# Display menu
echo -e "\n\033[1mAvailable recipients:\033[0m"
for i in "${!recipients[@]}"; do
    IFS=':' read -r email label <<< "${recipients[$i]}"
    printf "  [%d] %-20s %s\n" "$((i+1))" "$label" "$email"
done
echo -e "  [c] Enter custom email address"
echo -e "  [a] Send to ALL presets\n"

# Get selection
while true; do
    read -p "Select recipients (numbers/comma-separated, c=manual, a=all): " input
    case "$input" in
        [Cc]*) 
            read -p "Enter full email: " custom_email
            if [[ "$custom_email" =~ .+@.+\..+ ]]; then
                selected_emails=("$custom_email")
                break
            else
                echo "Invalid email format. Try again."
            fi
            ;;
        [Aa]*)
            selected_emails=()
            for item in "${recipients[@]}"; do
                selected_emails+=("${item%%:*}")
            done
            break
            ;;
        *)
            IFS=',' read -ra choices <<< "$input"
            selected_emails=()
            valid=true
            
            for choice in "${choices[@]}"; do
                num=$(echo "$choice" | tr -d '[:space:]')
                if [[ "$num" =~ ^[0-9]+$ && "$num" -ge 1 && "$num" -le "${#recipients[@]}" ]]; then
                    selected_emails+=("${recipients[$((num-1))]%%:*}")
                else
                    echo "Invalid selection: $num (must be 1-${#recipients[@]})"
                    valid=false
                fi
            done
            $valid && break
            ;;
    esac
done

# Send emails
if command -v mutt >/dev/null; then
    echo "$BODY" | mutt -s "$SUBJECT" -a "$XLSX_FILE" -a "$CSV_FILE" -- "${selected_emails[@]}"
    status=$?
elif command -v mail >/dev/null; then
    echo "$BODY" | mail -s "$SUBJECT" -A "$XLSX_FILE" -A "$CSV_FILE" "${selected_emails[@]}"
    status=$?
else
    notify-send "Error" "Install mutt or mailutils first"
    exit 1
fi

# Notify result
if [ $status -eq 0 ]; then
    notify-send "Success" "Sent to:\n${selected_emails[*]}\n\nAttached:\n$(basename "$XLSX_FILE")\n$(basename "$CSV_FILE")"
else
    notify-send "Error" "Failed to send (code $status)"
fi