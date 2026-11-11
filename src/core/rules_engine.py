def evaluate_cloudtrail_event(event_data):
    """
    Avalia um evento CloudTrail contra regras de segurança determinísticas.
    """
    rules_triggered = []
    
    # Regra 1: Desativação do MFA
    if event_data.get("eventName") == "DeactivateMFADevice":
        rules_triggered.append({
            "rule_id": "SEC-001",
            "severity": "HIGH",
            "description": "Dispositivo MFA desativado detetado."
        })
        
    # Regra 2: Acesso sem privilégios ou root login
    if event_data.get("userIdentity", {}).get("type") == "Root" and event_data.get("eventName") == "ConsoleLogin":
        rules_triggered.append({
            "rule_id": "SEC-002",
            "severity": "CRITICAL",
            "description": "Login efetuado com a conta Root."
        })
        
    return rules_triggered

if __name__ == "__main__":
    sample_event = {"eventName": "DeactivateMFADevice", "userIdentity": {"type": "IAMUser"}}
    alertas = evaluate_cloudtrail_event(sample_event)
    print(f"Regras avaliadas. Alertas gerados: {len(alertas)}")
