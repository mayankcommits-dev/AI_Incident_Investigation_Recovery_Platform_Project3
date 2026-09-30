def get_automation_health(automation_name: str) -> dict:

    health_data = {
        "InvoiceProcessingBot": {
            "status": "DEGRADED",
            "last_successful_run": "2026-09-28T08:45:00",
            "failed_jobs": 3
        },

        "PaymentReconciliationBot": {
            "status": "FAILED",
            "last_successful_run": "2026-09-28T07:30:00",
            "failed_jobs": 8
        },

        "OrderProcessingBot": {
            "status": "DEGRADED",
            "last_successful_run": "2026-09-28T09:10:00",
            "failed_jobs": 2
        }
    }

    return health_data.get(automation_name)



def get_automation_logs(automation_name: str) -> list[str]:

    logs = {
        "InvoiceProcessingBot": [
            "Invoice received successfully.",
            "OCR extraction started.",
            "OCR service request timed out after 30 seconds."
        ],

        "PaymentReconciliationBot": [
            "Payment reconciliation started.",
            "Authentication request sent.",
            "API returned 401 Unauthorized.",
            "Authentication token expired."
        ],

        "OrderProcessingBot": [
            "Order retrieved from queue.",
            "Queue connection attempt failed.",
            "Connection timed out after 20 seconds."
        ]
    }

    return logs.get(automation_name, [])


