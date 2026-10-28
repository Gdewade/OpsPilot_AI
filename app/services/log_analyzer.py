def analyze_logs(log_text: str) -> dict:
    lines = log_text.splitlines()

    errors = []
    warnings = []

    for line in lines:
        log_line = line.strip()

        if not log_line:
            continue

        upper_line = log_line.upper()

        if "ERROR" in upper_line or "CRITICAL" in upper_line:
            errors.append(log_line)

        elif "WARNING" in upper_line or "WARN" in upper_line:
            warnings.append(log_line)

    # Determine overall severity
    if any("CRITICAL" in line.upper() for line in errors):
        severity = "high"
    elif errors:
        severity = "high"
    elif warnings:
        severity = "medium"
    else:
        severity = "low"

    return {
        "total_lines": len(lines),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "severity": severity,
    }