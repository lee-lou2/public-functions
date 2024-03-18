from datetime import datetime, timedelta

import requests


account_auth_token = ""
employee_auth_token = ""


def get_leave_employees(target_date):
    """휴가자 조회"""
    # API URL
    api_url = "https://shiftee.io/api/batch"
    # HTTP Headers
    headers = {
        "cache-control": "no-cache",
        "content-type": "application/json",
        "cookie": f"shiftee_account_auth_token={account_auth_token}; shiftee_employee_auth_token={employee_auth_token};",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    }
    # Payload
    payload = {"employees": True}
    resp = requests.post(api_url, headers=headers, json=payload)
    resp.raise_for_status()

    employees = {
        employee.get("employee_id"): employee.get("last_name")
        + employee.get("first_name")
        for employee in resp.json().get("employees", [])
    }

    # 휴가 조회
    start_date = datetime.strptime(target_date, "%Y-%m-%d").date() - timedelta(days=1)
    start_date_str = start_date.strftime("%Y-%m-%dT00:00:00+09:00")
    end_date = datetime.strptime(target_date, "%Y-%m-%d").date() + timedelta(days=1)
    end_date_str = end_date.strftime("%Y-%m-%dT23:59:59+09:00")
    payload = {
        "leaves": {
            "employee_ids": list(employees.keys()),
            "date_ranges": [[start_date_str, end_date_str]],
        },
    }

    target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    resp = requests.post(api_url, headers=headers, json=payload)
    resp.raise_for_status()

    result = []
    exists_employee = []
    for leave in resp.json()["leaves"]:
        end_time = datetime.strptime(leave["end_time"], "%Y-%m-%dT%H:%M:%S%z").date()
        leave_type = leave["leave_type"]
        employee_id = leave["employee_id"]
        if target_date == end_time and employee_id not in exists_employee:
            result.append((leave_type, employees[employee_id]))
            exists_employee.append(employee_id)
    return result


# 검색할 날짜
today_date = datetime.today().strftime("%Y-%m-%d")
tomorrow_date = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

# 문자열 변환
today_leave_employees_string = "\n".join(
    [
        f"{employee_name} - {leave_type}"
        for leave_type, employee_name in get_leave_employees(today_date)
    ]
)
tomorrow_leave_employees_string = "\n".join(
    [
        f"{employee_name} - {leave_type}"
        for leave_type, employee_name in get_leave_employees(tomorrow_date)
    ]
)

message = f"""[{today_date} (오늘)부재알림]
{today_leave_employees_string}

[{tomorrow_date} (내일)부재알림]
{tomorrow_leave_employees_string}"""

print(message)
