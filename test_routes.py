from app import app

with app.app_context():
    print("Available routes:")
    for rule in app.url_map.iter_rules():
        if 'report' in rule.rule.lower():
            print(f"  {rule.rule} -> {rule.endpoint}")
