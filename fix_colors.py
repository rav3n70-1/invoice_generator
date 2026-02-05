with open('invoice_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace danger with error
content = content.replace("bg=self.c['danger']", "bg=self.c['error']")

with open('invoice_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed color references - replaced 'danger' with 'error'")
