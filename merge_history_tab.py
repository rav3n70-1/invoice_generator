with open('invoice_history_tab.py', 'r', encoding='utf-8') as f:
    hist_content = f.read()
    # Remove the comment header
    hist_content = hist_content.replace('# Invoice History Tab Implementation\n\n', '')

with open('invoice_app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# Find where to insert (before def main())
insert_pos = app_content.find('def main():')

# Create new content
new_content = app_content[:insert_pos] + hist_content + '\n\n' + app_content[insert_pos:]

# Write back
with open('invoice_app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('InvoiceHistoryTab class added successfully!')
